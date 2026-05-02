import os
import subprocess
import sys

from mtlogger import LogLevel, logger
from tqdm import tqdm

from _common import exit_with_prompt, get_chapter, print_error
from _sound_utils import play_notification_sound

def main():
  if len(sys.argv) > 1:
    folder = sys.argv[1]
  else:
    folder = prompt_parent_folder()

  if len(sys.argv) > 2:
    ranges = sys.argv[2]
  else:
    ranges = prompt_chapter_ranges()

  if folder and ranges:
    process_parent_folder(folder, ranges)

def prompt_parent_folder():
  parent_folder = input('Enter the path to the parent folder containing the chapter folders you want to prefix:\n')
  logger.log()
  if os.path.isdir(parent_folder):
    return parent_folder
  else:
    if parent_folder:
      logger.error(f'The specified path "{parent_folder}" is not a directory.')
    return None

def prompt_chapter_ranges():
  ranges_input = input('Enter the last chapter for each volume, separated by commas (e.g. 12,24,36):\n')
  logger.log()
  if not ranges_input:
    logger.error('No ranges were provided.')
    return None
  try:
    chapter_bounds = sorted([float(x.strip()) for x in ranges_input.split(',')])
  except Exception as ex:
    logger.error(f'Invalid input: {ex}')
    return None
  if len(chapter_bounds) < 1:
    logger.error('At least one boundary is required.')
    return None

  ranges = []
  prev = 0.0
  for b in chapter_bounds:
    ranges.append((prev + 1, b + 0.99))
    prev = b
  return ranges

def process_parent_folder(parent_folder, chapter_ranges):
  folders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]

  for folder in tqdm(folders, desc=f'Processing "{parent_folder}"'):
    chapter = get_chapter(folder)
    if not chapter:
        tqdm.write(logger.format(LogLevel.WARN, f'Skipping "{folder}". Chapter number could not be inferred.'))
        continue
    try:
      ch_num = float(chapter)
    except ValueError:
      continue

    for vol_index, (start, end) in enumerate(chapter_ranges, 1):
      if start <= ch_num <= end:
        prefix = f'Vol.{str(vol_index).zfill(2)}'
        if folder.startswith(prefix):
          break
        old_path = os.path.join(parent_folder, folder)
        new_path = os.path.join(parent_folder, prefix + ' ' + folder)
        os.rename(old_path, new_path)
        break

  play_notification_sound()
  logger.info(f'Finished processing "{parent_folder}".\n')

  merge_input = input('Merge volumes? (y)/n\n').strip().lower()
  if merge_input != 'n':
    merge_script = os.path.join(os.path.dirname(__file__), 'merge_volumes.py')
    subprocess.run([sys.executable, merge_script, parent_folder], check = True)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()

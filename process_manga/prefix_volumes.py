import os
import re
import subprocess
import sys
import winsound

from mtlogger import Fore, logger
from mtprompt import Prompt
from tqdm import tqdm

from _common import ITEM_EXTENSIONS, get_chapter

def main():
  if len(sys.argv) > 1:
    folder = sys.argv[1]
  else:
    folder = Prompt.dir(
      'Enter the path to the parent folder containing the chapter folders you want to prefix'
    )

  if len(sys.argv) > 2:
    ranges = sys.argv[2]
  else:
    ranges = prompt_chapter_ranges(folder)

  if folder and ranges:
    process_parent_folder(folder, ranges)

def prompt_chapter_ranges(
  folder_path: str,
):
  ranges_input = Prompt.str(f'Enter the volume ranges. Supported formats:\n{logger.colorize(Fore.CYAN, " n1, n2, n3, ..., n99")}\n{logger.colorize(Fore.LIGHTBLACK_EX, "  Last chapter for each volume, separated by commas (e.g. 12,24,36)")}\n{logger.colorize(Fore.CYAN, " [n]")}\n{logger.colorize(Fore.LIGHTBLACK_EX, "  fixed chapter count per volume (e.g. [12])")}\n')

  match = re.fullmatch(r'\[(\d+)\]', ranges_input.strip())
  if match:
    step = int(match.group(1))
    items = sorted([
      item
      for item in os.listdir(folder_path)
      if os.path.isdir(os.path.join(folder_path, item))
      or os.path.splitext(item)[1].lower().endswith(tuple(ITEM_EXTENSIONS))
    ])
    lastChapter = int(get_chapter(items[-1]))
    chapter_bounds = [i for i in range(step, lastChapter + step, step)]
    chapter_bounds[-1] = lastChapter
    ranges = []
    prev = 0.0
    for b in chapter_bounds:
      ranges.append((prev + 1, b + 0.99))
      prev = b
    return ranges

  try:
    chapter_bounds = sorted([float(x.strip()) for x in ranges_input.split(',')])
  except Exception as ex:
    logger.error(f'Invalid input:\n{ex}')
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

def process_parent_folder(
  parent_folder_path: str,
  chapter_ranges: list,
):
  folders = [f for f in os.listdir(parent_folder_path) if os.path.isdir(os.path.join(parent_folder_path, f))]

  for folder in tqdm(folders, desc=f'Processing "{parent_folder_path}"'):
    chapter = get_chapter(folder)
    if not chapter:
      tqdm.write(logger.formatWarn(f'Skipping "{folder}". Chapter number could not be inferred.'))
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
        old_folder_path = os.path.join(parent_folder_path, folder)
        new_folder_path = os.path.join(parent_folder_path, prefix + ' ' + folder)
        os.rename(old_folder_path, new_folder_path)
        break

  winsound.MessageBeep()
  logger.success(f'Finished prefixing volumes in "{parent_folder_path}".\n')

  merge_input = Prompt.bool('Merge volumes?', default=True)
  if merge_input:
    merge_script = os.path.join(os.path.dirname(__file__), 'merge_volumes.py')
    subprocess.run([sys.executable, merge_script, parent_folder_path], check = True)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
    Prompt.enter_to_exit()

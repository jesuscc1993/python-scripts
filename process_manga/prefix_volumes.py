import os
import re

from tqdm import tqdm

from _sound_utils import play_notification_sound

def main():
  folder = prompt_parent_folder()
  if folder:
    print('')
    ranges = prompt_chapter_ranges()
  if ranges:
    print('')
    process_parent_folder(folder, ranges)
    main()

def prompt_parent_folder():
  parent_folder = input('Enter the path to the parent folder containing the chapter folders you want to prefix:\n')
  if os.path.isdir(parent_folder):
    return parent_folder
  else:
    if parent_folder:
      print(f'The specified path "{parent_folder}" is not a directory.')
    return None

def prompt_chapter_ranges():
  ranges_input = input('Enter the last chapter for each volume, separated by commas (e.g. 12,24,36):\n')
  if not ranges_input:
    return [(0, float('inf'))]
  try:
    chapter_bounds = sorted([float(x.strip()) for x in ranges_input.split(',')])
  except Exception as e:
    print(f'Invalid input: {e}')
    return None
  if len(chapter_bounds) < 1:
    print('At least one boundary is required')
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
  print(f'Finished processing "{parent_folder}".\n')

def get_chapter(folder_name):
  match = re.search(r'(Ch(?:apter)?|Ep(?:isode)?)\.?\s*(\d+(?:\.\d+)?)', folder_name, re.IGNORECASE)
  return match.group(2) if match else None

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

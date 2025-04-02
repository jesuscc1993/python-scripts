import os
import shutil
import re

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _sound_utils import play_notification_sound

def main():
  parent_folder = input('Enter the path to the parent folder containing the chapter folders:\n').strip('" ')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    find_missing_chapters(parent_folder)
    play_notification_sound()
    print(f'')
  main()

def find_missing_chapters(directory):
  pattern = re.compile(r'(?:Ch(?:apter)?|Ep(?:isode)?)\.?\s*(\d+)', re.IGNORECASE)
  chapters = set()

  for entry in os.scandir(directory):
    if entry.is_file() or entry.is_dir():
      match = pattern.search(entry.name)
      if match:
        chapters.add(int(match.group(1)))

  if not chapters:
    print('No chapters found.')
    return

  missing_chapters = sorted(set(range(1, max(chapters) + 1)) - chapters)
  if missing_chapters:
    print(f'\nChapters missing in "{directory}":')
    for ch in missing_chapters:
      print(f' {ch:03d}')
  else:
    print('No missing chapters found.')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')
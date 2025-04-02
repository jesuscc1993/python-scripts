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
  pattern = re.compile(r'(?:Vol(?:ume)?\.?\s*(\d+))?.*?(Ch(?:apter)?|Ep(?:isode)?)\.?\s*(\d+)', re.IGNORECASE)
  chapters = set()

  for entry in os.scandir(directory):
    if entry.is_file() or entry.is_dir():
      match = pattern.search(entry.name)
      if match:
        chapters.add(int(match.group(3)))

  if not chapters:
    print('No chapters found.')
    return

  min_chapter, max_chapter = min(chapters), max(chapters)
  missing_chapters = sorted(set(range(min_chapter, max_chapter + 1)) - chapters)

  if missing_chapters:
    print(f'Missing chapters: {missing_chapters}.')
  else:
    print('No missing chapters found.')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')
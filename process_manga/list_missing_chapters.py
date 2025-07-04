import os
import re
import sys

from _common import exit_with_prompt, print_error, select_parent_folder

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the chapter folders:\n', process_parent_folder)

def process_parent_folder(directory):
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
    print(f'\nNo chapters found missing in "{directory}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()
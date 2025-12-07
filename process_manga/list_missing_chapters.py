import os
import re
import sys

from mtlogger import logger

from _common import exit_with_prompt, print_error, select_parent_folder

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the chapter folders:\n', process_parent_folder)

def process_parent_folder(directory):
  pattern = re.compile(r'(?:Ch(?:apter)?|Ep(?:isode)?)\.?\s*(\d+)', re.IGNORECASE)
  found_chapters = set()

  for entry in os.scandir(directory):
    match = pattern.search(entry.name)
    if match:
      found_chapters.add(int(match.group(1)))

  if not found_chapters:
    logger.log('No chapters found.')
    return

  expected_chapters = set(range(1, max(found_chapters) + 1))
  missing_chapters = sorted(expected_chapters - found_chapters)
  if missing_chapters:
    logger.log(f'\nChapters missing in "{directory}":')
    for ch in missing_chapters:
      logger.log(f' {ch:03d}')
  else:
    logger.log(f'\nNo chapters found missing in "{directory}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()
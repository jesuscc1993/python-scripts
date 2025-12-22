import os
import re
import sys

from mtlogger import logger

from _common import CH_REGEX, exit_with_prompt, print_error, select_parent_folder

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the chapter folders:\n',
      process_parent_folder,
      { 'log_success': False, 'loop': False }
    )

def process_parent_folder(directory):
  directory_name = os.path.basename(directory)
  pattern = re.compile(CH_REGEX, re.IGNORECASE)
  found_chapters = set()

  for entry in os.scandir(directory):
    match = pattern.search(entry.name)
    if match:
      found_chapters.add(float(match.group(1)))

    if entry.is_dir():
      process_chapter_folder(entry.path)

  if not found_chapters:
    logger.log(f'No chapters found in "{directory_name}".')
    return

  expected_chapters = set(range(1, int(max(found_chapters)) + 1))
  missing_chapters = expected_chapters - found_chapters
  if missing_chapters:
    logger.log(
      f'\nChapters missing in "{directory_name}": '
      f'{" ".join(f"{ch:03d}" for ch in sorted(missing_chapters))}'
    )
  else:
    logger.log(f'\nNo chapters found missing in "{directory}".')

def process_chapter_folder(directory):
  directory_name = os.path.basename(directory)
  pattern = re.compile(r'(\d+)', re.IGNORECASE)
  found_pages = set()

  for entry in os.scandir(directory):
    if entry.is_file():
      match = pattern.search(entry.name)
      if match:
        found_pages.add(float(match.group(1)))

  if not found_pages:
    logger.log(f'No pages found in "{directory_name}".')
    return

  expected_pages = set(range(1, int(max(found_pages)) + 1))
  missing_pages = expected_pages - found_pages
  if missing_pages:
    logger.log(
      f'Pages missing in "{directory_name}": '
      f'{" ".join(f"{p:02d}" for p in sorted(missing_pages))}'
    )

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()
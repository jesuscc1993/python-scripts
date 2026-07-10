import os
import re
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import get_chapter, select_parent_folder

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the chapter folders:\n',
      process_parent_folder,
      { 'log_success': False }
    )

def process_parent_folder(directory):
  directory_name = os.path.basename(directory)
  found_chapters = set()

  for entry in sorted(os.scandir(directory), key = get_sort_key):
    chapter = get_chapter(entry.name)
    if chapter:
      found_chapters.add(float(chapter))

    if entry.is_dir():
      process_chapter_folder(entry.path, chapter)

  if not found_chapters:
    logger.trace(f'No chapters found in "{directory_name}".')
    return

  expected_chapters = set(range(1, int(max(found_chapters)) + 1))
  missing_chapters = expected_chapters - found_chapters
  if missing_chapters:
    logger.warn(
      f'\nChapters missing in "{directory_name}": '
      f'{" ".join(format_chapter(ch) for ch in sorted(missing_chapters))}'
    )
  else:
    logger.success(
      f'No chapters found missing in "{directory}".',
      prefix_newline=True
    )

def process_chapter_folder(directory, chapter):
  pattern = re.compile(r'(\d+)', re.IGNORECASE)
  found_pages = set()

  for entry in os.scandir(directory):
    if entry.is_file():
      match = pattern.search(entry.name)
      if match:
        found_pages.add(float(match.group(1)))

  if not found_pages:
    logger.warn(f'- [Ch.{format_chapter(chapter)}] All pages missing.')
    return

  expected_pages = set(range(1, int(max(found_pages)) + 1))
  missing_pages = expected_pages - found_pages
  if missing_pages:
    logger.warn(
      f'- [Ch.{format_chapter(chapter)}] {len(missing_pages):02d} page(s) missing: '
      f'{" ".join(f"{p:02d}" for p in sorted(missing_pages))}'
    )

def get_sort_key(entry):
  chapter = get_chapter(entry.name)
  return (0, float(chapter)) if chapter is not None else (1, entry.name.lower())

def format_chapter(chapter):
  integer, dot, decimal = f'{float(chapter):g}'.partition('.')
  return f'{int(integer):03d}{dot}{decimal}'

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
    Prompt.enter_to_exit()

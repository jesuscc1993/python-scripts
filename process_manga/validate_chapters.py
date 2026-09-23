import itertools
import os
import re
import sys

from mtlogger import logger
from mtprompt import Prompt, to_bool, to_dir

from _common import get_chapter, select_parent_folder

def main():
  if len(sys.argv) > 1:
    params = [to_dir(sys.argv[1])]
    if len(sys.argv) > 2: params.append(to_bool(sys.argv[2]))
    if len(sys.argv) > 3: params.append(to_bool(sys.argv[3]))
    process_parent_folder(*params)
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the chapter folders:\n',
      process_parent_folder,
      { 'log_success': False }
    )

def process_parent_folder(
  dir_path: str,
  prompt_for_deletion = True,
  recursive = True,
):
  dir_name = os.path.basename(dir_path)
  entries = sorted(os.scandir(dir_path), key = get_sort_key)
  found_chapters = set()

  missing_chapters: list[float] = []
  incomplete_chapters: list[float] = []
  empty_chapters: list[float] = []

  for entry in entries:
    chapter = get_chapter(entry.name)
    if chapter:
      found_chapters.add(float(chapter))

  if found_chapters:
    logger.hr('·')
    logger.log(f'Processing "{dir_path}"...')
  else:
    found_subfolder_chapters = False

    if recursive:
      for entry in os.scandir(dir_path):
        if entry.is_dir():
          subfolder_result = process_parent_folder(entry.path, recursive=False)
          found_subfolder_chapters = found_subfolder_chapters or subfolder_result
      if not found_subfolder_chapters:
        logger.trace(f'No chapters found in "{dir_name}", trying subfolders instead.')

    return found_subfolder_chapters

  missing_chapters = find_missing(found_chapters)
  missing_chapter_pages_dict: dict[float, list[float]] = {}

  for entry in entries:
    chapter = get_chapter(entry.name)
    if chapter and entry.is_dir():
      missing_chapter_pages = get_missing_chapter_pages(entry.path, chapter)
      if missing_chapter_pages:
        incomplete_chapters.append(float(chapter))
        missing_chapter_pages_dict[float(chapter)] = missing_chapter_pages
      if not os.listdir(entry.path):
        empty_chapters.append(entry)

  logger.log()

  is_problematic = bool(missing_chapters or incomplete_chapters or empty_chapters)
  if not is_problematic:
    logger.success(f'No chapters nor pages detected missing in "{dir_name}".')
    return True

  logger.warn(
    f'Found issues for "{dir_name}".\n'
    f'* Detected chapter range: {format_chapter(1)}-{format_chapter(max(found_chapters))}'
  )

  if missing_chapters:
    logger.warn(
      f'* Missing chapters: '
      f'{" ".join(format_number_ranges(missing_chapters))}'
    )

  if incomplete_chapters:
    logger.warn(
      f'* Incomplete chapters: '
      f'{" ".join(format_number_ranges(incomplete_chapters))}'
    )
  if missing_chapter_pages_dict:
    for chapter, missing_pages in missing_chapter_pages_dict.items():
      logger.warn(
        f'  * [{format_chapter(chapter)}] '
        f'Is missing {len(missing_pages)} page{"s" if len(missing_pages) != 1 else ""}: '
        f'{" ".join(f"{p:02d}" for p in missing_pages)}'
      )

  if empty_chapters:
    logger.warn(
      f'* Empty chapters: '
      f'{" ".join(format_number_ranges(empty_chapters))}'
    )

  if (
    empty_chapters and
    prompt_for_deletion is not False and
    Prompt.bool('Delete empty chapters?')
  ):
    for entry in empty_chapters:
      os.rmdir(entry.path)
      logger.success(f'Deleted empty chapter folder: "{entry.name}"')

  return True

def get_missing_chapter_pages(
  dir_path: str,
  chapter: str,
):
  pattern = re.compile(r'(\d+)', re.IGNORECASE)
  found_pages = set()

  for entry in os.scandir(dir_path):
    if entry.is_file():
      match = pattern.search(entry.name)
      if match:
        found_pages.add(float(match.group(1)))

  if not found_pages:
    logger.warn(f'- [Ch.{format_chapter(chapter)}] All pages missing.')
    return True

  return find_missing(found_pages)

def get_sort_key(
  entry: os.DirEntry,
):
  chapter = get_chapter(entry.name)
  return (0, float(chapter)) if chapter is not None else (1, entry.name.lower())

def find_missing(
  found: set[float],
):
  expected = range(1, int(max(found)) + 1)
  return [n for n in expected if n not in found]

def format_chapter(
  chapter: str,
):
  integer, dot, decimal = f'{float(chapter):g}'.partition('.')
  return f'{int(integer):03d}{dot}{decimal}'

def format_number_ranges(
  numbers: list[float],
):
  groups = itertools.groupby(enumerate(numbers), lambda pair: pair[1] - pair[0])
  ranges = [[number for _, number in group] for _, group in groups]

  return [
    format_chapter(group[0]) if len(group) == 1 else f'{format_chapter(group[0])}-{format_chapter(group[-1])}'
    for group in ranges
  ]

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

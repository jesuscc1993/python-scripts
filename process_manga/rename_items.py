import os
import re
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm
from typing import Callable

from _common import CHAPTER_NUMBER_REGEX, ENDING_REGEX, EPILOGUE_REGEX, IMAGE_EXTENSIONS, INTEGER_REGEX, SEASON_REGEX, SIDE_STORY_REGEX, SPECIAL_REGEX, VOLUME_NUMBER_REGEX, zfill_float

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    prompt_parent_folder()

def prompt_parent_folder():
  parent_folder = Prompt.dir(
    'Enter the path to the parent folder containing the chapter folders you want to rename'
  )

  process_parent_folder(parent_folder)

def process_parent_folder(
  parent_folder_path: str,
):
  for root, dirs, files in os.walk(parent_folder_path, topdown = False):
    all_items = files + dirs

    with ThreadPoolExecutor() as executor:
      list(tqdm(executor.map(lambda item: process_item(root, item), all_items), total = len(all_items), desc=f'Processing "{root}"'))

  logger.success(f'Finished renaming items in "{parent_folder_path}".')

def process_item(
  parent_folder_path: str,
  item_name: str,
):
  item_path = os.path.join(parent_folder_path, item_name)
  new_name = get_processed_name(item_path)
  if new_name != item_name:
    new_path = os.path.join(parent_folder_path, new_name)
    os.rename(item_path, new_path)

def get_processed_name(
  item_path: str,
):
  is_dir = os.path.isdir(item_path)
  base_name = os.path.basename(item_path)
  new_name = base_name

  if not is_dir:
    new_name, ext = os.path.splitext(new_name)
    ext = ext.lower()

    # skip images
    if ext.lstrip('.') in IMAGE_EXTENSIONS:
      return base_name

  else:
    ext = ''

  # remove item index
  new_name = replace(r'\s*\[\d*\]\s*', ' ', new_name)

  # remove unnecessary tags
  new_name = replace(r'\s*\(official\)\s*', ' ', new_name)

  # prettify volume number
  new_name = replace(
    rf'{VOLUME_NUMBER_REGEX}',
    lambda match: f'Vol.{zfill_float(match.group(1), 2)}',
    new_name
  )

  # prettify chapter number
  new_name = replace(
    rf'{CHAPTER_NUMBER_REGEX}',
    lambda match: f'Ch.{zfill_float(match.group(1), 3)}',
    new_name
  )

  # shorten common words
  new_name = replace(rf'{SEASON_REGEX}{INTEGER_REGEX}', r'S\1', new_name)
  new_name = replace(rf'{EPILOGUE_REGEX}{INTEGER_REGEX}', r'EP\1', new_name)
  new_name = replace(rf'{SIDE_STORY_REGEX}{INTEGER_REGEX}', r'SS\1', new_name)
  new_name = replace(rf'{SPECIAL_REGEX}{INTEGER_REGEX}', r'SP\1', new_name)
  new_name = replace(rf'{ENDING_REGEX}', r'END', new_name)

  # fix duplicate chapter number, sometimes a result of the scraper
  new_name = replace(r'(Ch\.\d+) - \1', r'\1', new_name)

  # remove remaining unnecessary whitespaces
  new_name = replace(r'\s+', ' ', new_name).strip()

  if not is_dir:
    # rename ZIP volumes as CBZ
    # do not rename chapters as they have too much of a performance impact
    if (ext == '.zip' and 'Vol.' in new_name):
      ext = '.cbz'

  return new_name + ext

def replace(
  pattern: str,
  repl: str | Callable,
  string: str,
  flags=re.IGNORECASE,
):
  return re.sub(pattern, repl, string, flags=flags)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

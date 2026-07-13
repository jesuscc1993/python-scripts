import os
import re
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm

from _common import VOLUME_REGEX, CHAPTER_REGEX

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

def process_parent_folder(parent_folder):
  for root, dirs, files in os.walk(parent_folder, topdown = False):
    all_items = files + dirs

    with ThreadPoolExecutor() as executor:
      list(tqdm(executor.map(lambda item: process_item(root, item), all_items), total = len(all_items), desc=f'Processing "{root}"'))

  logger.success(f'Finished renaming items in "{parent_folder}".')

def process_item(root, item_name):
  item_path = os.path.join(root, item_name)
  new_name = get_processed_name(item_path)
  if new_name != item_name:
    new_path = os.path.join(root, new_name)
    os.rename(item_path, new_path)

def get_processed_name(item_path):
  is_dir = os.path.isdir(item_path)
  new_name = os.path.basename(item_path)

  if not is_dir:
    new_name = re.sub(r'\s*\{.*\}', '', new_name)
    new_name, ext = os.path.splitext(new_name)

    # save only volumes as CBZ
    # saving all chapters has too much of a performance impact
    if ('Vol.' in new_name):
      ext = '.cbz'
  else:
    ext = ''

  new_name = re.sub(r'\s*\(Official\)', '', new_name)
  new_name = re.sub(r'\s+', ' ', new_name)

  new_name = re.sub(
    rf'\b({CHAPTER_REGEX})\b\.?\s*(\d+)',
    lambda match: f'Ch.{int(match.group(2)):03}',
    new_name,
    flags = re.IGNORECASE
  )
  new_name = re.sub(r'(Ch\.\d+) - \1', r'\1', new_name.strip())

  new_name = re.sub(
    rf'\b({VOLUME_REGEX})\b\.?\s*(\d+)',
    lambda match: f'Vol.{int(match.group(2)):02}',
    new_name,
    flags = re.IGNORECASE
  )

  new_name = re.sub(
    r'(?:-\s*)?\[?(?:(?:the\s+)?end|series finale)\]?',
    '[END]',
    new_name,
    flags = re.IGNORECASE
  )

  return new_name.strip() + ext

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

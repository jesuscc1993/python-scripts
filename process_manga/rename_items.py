import os
import re
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

from _common import VOLUME_REGEX, CHAPTER_REGEX, exit_with_prompt, print_error
from _sound_utils import play_notification_sound

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    prompt_parent_folder()

def prompt_parent_folder():
  parent_folder = input('Enter the path to the parent folder containing the chapter folders you want to rename:\n')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    logger.error(f'The specified path "{parent_folder}" is not a directory.')
  else:
    process_parent_folder(parent_folder)
    play_notification_sound()
    exit_with_prompt()

def process_parent_folder(parent_folder):
  for root, dirs, files in os.walk(parent_folder, topdown = False):
    all_items = files + dirs

    with ThreadPoolExecutor() as executor:
      list(tqdm(executor.map(lambda item: process_item(root, item), all_items), total = len(all_items), desc=f'Processing "{root}"'))

  logger.info(f'Finished processing "{parent_folder}".')

def process_item(root, item_name):
  new_name = get_processed_name(item_name)
  if item_name != new_name:
    old_path = os.path.join(root, item_name)
    new_path = os.path.join(root, new_name)
    os.rename(old_path, new_path)

def get_processed_name(name):
  new_name = re.sub(r'\s+', ' ', name).strip()

  new_name = re.sub(
    rf'\b({CHAPTER_REGEX})\b\.?\s*(\d+)',
    lambda match: f'Ch.{int(match.group(2)):03}',
    new_name,
    flags = re.IGNORECASE
  )

  new_name = re.sub(
    rf'\b({VOLUME_REGEX})\b\.?\s*(\d+)',
    lambda match: f'Vol.{int(match.group(2)):02}',
    new_name,
    flags = re.IGNORECASE
  )

  return new_name

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()
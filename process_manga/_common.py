import os
import re

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

from _image_utils import is_image_file
from _sound_utils import play_notification_sound

NUMBER_REGEX = r'\.?\s*(\d+(?:\.\d+)?)'
VOLUME_REGEX = r'Vol(?:ume)?'
CHAPTER_REGEX = r'Ch(?:ap(?:ter)?)?|Ep(?:isode)?'
VOLUME_NUMBER_REGEX = rf'(?:{VOLUME_REGEX}){NUMBER_REGEX}'
CHAPTER_NUMBER_REGEX  = rf'(?:{CHAPTER_REGEX}){NUMBER_REGEX}'

def select_parent_folder(prompt, callback, options = {}):
  log_success = options.get('log_success', False)
  loop = options.get('loop', True)

  parent_folder = input(prompt).strip(' "\'')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    logger.error(f'The specified path "{parent_folder}" is not a directory.')
  else:
    callback(parent_folder)
    play_notification_sound()

  if log_success:
    logger.log(f'Finished processing "{parent_folder}".\n')

  if loop:
    select_parent_folder(prompt, callback)
  else:
    input('')

def process_folder_images(folder_path, callback):
  files_to_process = []

  for root, _, files in os.walk(folder_path):
    for file in files:
      if is_image_file(file):
        file_path = os.path.join(root, file)
        files_to_process.append(file_path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{folder_path}"') as progress:
    for _ in executor.map(callback, files_to_process):
      progress.update(1)

def delete_empty_folders(folder_path):
  for root, dirs, _ in os.walk(folder_path, topdown = False):
    for dir_name in dirs:
      dir_path = os.path.join(root, dir_name)
      try:
        os.rmdir(dir_path)
      except OSError:
        pass

def get_volume_and_chapter(filename):
  vol_match = re.search(VOLUME_NUMBER_REGEX, filename, re.IGNORECASE)
  ch_match  = re.search(CHAPTER_NUMBER_REGEX, filename, re.IGNORECASE)
  volume  = vol_match.group(1) if vol_match else None
  chapter = ch_match.group(1) if ch_match else None
  return (volume, chapter)

def get_chapter(filename):
  ch_match = re.search(CHAPTER_NUMBER_REGEX, filename, re.IGNORECASE)
  chapter = ch_match.group(1) if ch_match else None
  return chapter

def print_error(error):
  logger.error(f'An unexpected error occurred: {error}')

def exit_with_prompt():
  input('Press Enter to exit...')

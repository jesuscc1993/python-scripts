import os
import re
import subprocess
import winsound

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm

from _image_utils import is_image_file

NUMBER_REGEX = r'\.?\s*(\d+(?:\.\d+)?)'
VOLUME_REGEX = r'Vol(?:ume)?'
CHAPTER_REGEX = r'Ch(?:ap(?:ter)?)?|Ep(?:isode)?|Ep(?:ilogue)?|Sp(?:ecial)?'
VOLUME_NUMBER_REGEX = rf'(?:{VOLUME_REGEX}){NUMBER_REGEX}'
CHAPTER_NUMBER_REGEX  = rf'(?:{CHAPTER_REGEX}){NUMBER_REGEX}'
ITEM_EXTENSIONS = ['cbz', 'zip']

def select_parent_folder(prompt, callback, options = {}):
  prompt = prompt or 'Enter the path to the parent folder you want to process:\n'
  log_success = options.get('log_success', False)
  loop = options.get('loop', True)

  parent_folder = input(prompt).strip(' "\'')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    logger.error(f'The specified path "{parent_folder}" is not a directory.')
  else:
    callback(parent_folder)
    winsound.MessageBeep()

  if log_success:
    logger.success(f'Finished processing "{parent_folder}".\n')

  if loop:
    logger.hr()
    select_parent_folder(prompt, callback)
  else:
    Prompt.enter_to_exit()

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

def run_scripts_in_sequence(script_names, parent_folder):
  env = os.environ.copy()
  env['NO_ENTER_TO_EXIT'] = '1'

  for script in script_names:
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), script + '.py'))

    logger.trace(f'\nRunning {script}:')
    subprocess.run(['python', abs_path, parent_folder], env=env)

  logger.info(
    f'Finished batch running scripts on "{parent_folder}".\n',
    prefix_newline=True
  )

import os
import re
import subprocess
import winsound

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm
from typing import Callable

from _image_utils import is_image_file

INTEGER_REGEX = r'\.?\s*(\d+)'
NUMBER_REGEX = r'\.?\s*(\d+(?:\.\d+)?)'

VOLUME_REGEX = r'\bVol(?:ume)?\b'
SEASON_REGEX = r'\bSeason\b'
CHAPTER_REGEX = r'\b(?:Ch(?:ap(?:ter)?)?|Ep(?:isode)?)\b'
EPILOGUE_REGEX = r'\bEp(?:ilogue)?\b'
SPECIAL_REGEX = r'\bSp(?:ecial)?\b'
ENDING_REGEX = r'\bEnd(?:ing)?\b'
SIDE_STORY_REGEX = r'\bSide Story\b'

VOLUME_NUMBER_REGEX = rf'{VOLUME_REGEX}{NUMBER_REGEX}'
CHAPTER_NUMBER_REGEX  = rf'{CHAPTER_REGEX}{NUMBER_REGEX}'

ITEM_EXTENSIONS = ['cbz', 'zip']
IMAGE_EXTENSIONS = ['webp', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif']

def select_parent_folder(
  prompt: str,
  callback: Callable,
  options: dict = {},
):
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

def process_folder_images(
  folder_path: str,
  callback: Callable,
):
  files_to_process = []

  for root, _, files in os.walk(folder_path):
    for file in files:
      if is_image_file(file):
        file_path = os.path.join(root, file)
        files_to_process.append(file_path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{folder_path}"') as progress:
    for _ in executor.map(callback, files_to_process):
      progress.update(1)

def delete_empty_folders(
  folder_path: str,
):
  for root, dirs, _ in os.walk(folder_path, topdown = False):
    for dir_name in dirs:
      dir_path = os.path.join(root, dir_name)
      try:
        os.rmdir(dir_path)
      except OSError:
        pass

def get_volume_and_chapter(
  filename: str,
):
  vol_match = re.search(VOLUME_NUMBER_REGEX, filename, re.IGNORECASE)
  ch_match = re.search(CHAPTER_NUMBER_REGEX, filename, re.IGNORECASE)
  volume = float(vol_match.group(1)) if vol_match else None
  chapter = float(ch_match.group(1)) if ch_match else None
  return (volume, chapter)

def get_chapter(
  filename: str,
):
  ch_match = re.search(CHAPTER_NUMBER_REGEX, filename, re.IGNORECASE)
  chapter = ch_match.group(1) if ch_match else None
  return chapter

def run_scripts_in_sequence(
  script_commands: list,
  parent_folder_path: str,
):
  env = os.environ.copy()
  env['NO_ENTER_TO_EXIT'] = '1'

  for script_command in script_commands:
    script, *arg_tokens = script_command.split(' ')
    args = [parent_folder_path if token == '$dir' else token for token in arg_tokens]
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), script + '.py'))

    logger.trace(f'\nRunning {script}:')
    subprocess.run(['python', abs_path, *args], env=env)

  logger.info(
    f'Finished batch running scripts on "{parent_folder_path}".\n',
    prefix_newline=True
  )

def zfill_float(
  value: float |str,
  width: int,
):
  parts = f'{float(value):g}'.split('.')
  return parts[0].zfill(width) + ('.' + parts[1] if len(parts) > 1 else '')

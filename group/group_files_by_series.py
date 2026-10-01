import os
import re
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt, to_bool, to_dir
from tqdm import tqdm

from _common import FILE_BLACKLIST, find_files_to_process, group_files

def main():
  parent_dir = to_dir(sys.argv[1]) if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the files you want to group')
  normalize_names = to_bool(sys.argv[2]) if len(sys.argv) > 2 else False

  files_to_process = find_files_to_process(parent_dir, should_process_item)

  if normalize_names:
    normalize_file_names(files_to_process, parent_dir)
    files_to_process = find_files_to_process(parent_dir, should_process_item)

  group_files(parent_dir, files_to_process, get_group_name)

def should_process_item(
  item_path: str,
):
  if not os.path.isfile(item_path):
    return False

  for pattern in FILE_BLACKLIST:
    if re.fullmatch(pattern, os.path.basename(item_path)):
      return False

  return True

def normalize_file_names(
  files_to_process: list,
  parent_folder_path: str,
):
  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{parent_folder_path}"') as progress:
    for _ in executor.map(lambda item_path: normalize_file_name(item_path, parent_folder_path), files_to_process):
      progress.update(1)

  logger.success(f'Finished normalizing file names in "{parent_folder_path}".\n')

def normalize_file_name(
  item_path: str,
  parent_folder_path: str,
):
  dst = os.path.join(parent_folder_path, get_normalized_name(os.path.basename(item_path)))
  os.rename(item_path, dst)

def get_group_name(
  file_path: str,
):
  file_name = get_normalized_name(os.path.basename(file_path))
  parts = re.split(r'(?:\s+-\s+|S\d+)', file_name)
  group_name = parts[0] if len(parts) > 1 else file_name
  return os.path.splitext(group_name)[0].strip()

def get_normalized_name(
  file_name: str,
):
  name, ext = os.path.splitext(file_name)
  name = re.sub(r'[\(\[\{].*?[\)\]\}]', '', name)
  name = re.sub(r'\s+', ' ', name).strip()
  return f'{name}{ext}'

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

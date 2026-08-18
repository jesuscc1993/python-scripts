import os
import shutil

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm
from typing import Callable

FILE_BLACKLIST = [
  r'cover.jpg',
  r'desktop.ini',
  r'folder.jpg',
  r'.*\.url',
  r'.*\.lnk'
]

def process_parent_folder(
  parent_folder_path: str,
  should_process_item: Callable,
  get_group_name: Callable,
):
  files_to_process = []

  for item in os.listdir(parent_folder_path):
    item_path = os.path.join(parent_folder_path, item)
    if should_process_item(item_path):
      group_name = get_group_name(item_path)
      if group_name:
        output_path = os.path.join(parent_folder_path, group_name)
        if not os.path.exists(output_path):
          os.makedirs(output_path)
        files_to_process.append((item_path, output_path))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{parent_folder_path}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

  logger.success(f'Finished grouping files in "{parent_folder_path}".')

def process_file(
  params: tuple,
):
  src, target_folder = params
  dest = os.path.join(target_folder, os.path.basename(src))
  shutil.move(src, dest)

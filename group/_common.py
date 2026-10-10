import os
import shutil

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm
from collections.abc import Callable

FILE_BLACKLIST = [
  r'cover.jpg',
  r'desktop.ini',
  r'folder.jpg',
  r'.*\.url',
  r'.*\.lnk',
]


def find_files_to_process(
  parent_folder_path: str,
  should_process_item: Callable,
):
  files_to_process = []

  for item in os.listdir(parent_folder_path):
    item_path = os.path.join(parent_folder_path, item)
    if should_process_item(item_path):
      files_to_process.append(item_path)

  return files_to_process


def group_files(
  parent_folder_path: str,
  files_to_process: list,
  get_group_name: Callable,
):
  with (
    ThreadPoolExecutor() as executor,
    tqdm(
      total=len(files_to_process), desc=f'Processing "{parent_folder_path}"'
    ) as progress,
  ):
    for _ in executor.map(
      lambda item_path: process_file(
        item_path, parent_folder_path, get_group_name
      ),
      files_to_process,
    ):
      progress.update(1)

  logger.success(f'Finished grouping files in "{parent_folder_path}".')


def process_file(
  item_path: str,
  parent_folder_path: str,
  get_group_name: Callable,
):
  group_name = get_group_name(item_path)
  if not group_name:
    return

  target_folder = os.path.join(parent_folder_path, group_name)
  os.makedirs(target_folder, exist_ok=True)
  dest = os.path.join(target_folder, os.path.basename(item_path))
  shutil.move(item_path, dest)

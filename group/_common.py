import os
import shutil

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

FILE_BLACKLIST = [
  r'desktop.ini',
  r'.*\.url',
  r'.*\.lnk'
]

def process_parent_folder(root_dir, should_process_item, get_group_name):
  files_to_process = []

  for item in os.listdir(root_dir):
    item_path = os.path.join(root_dir, item)
    if should_process_item(item_path):
      group_name = get_group_name(item_path)
      if group_name:
        output_path = os.path.join(root_dir, group_name)
        if not os.path.exists(output_path):
          os.makedirs(output_path)
        files_to_process.append((item_path, output_path))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

  logger.info(f'Successfully grouped files in "{root_dir}".')

def process_file(params):
  src, target_folder = params
  dest = os.path.join(target_folder, os.path.basename(src))
  shutil.move(src, dest)

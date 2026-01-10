import os
import re
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

from _common import select_parent_folder, process_file

FILE_BLACKLIST = [
  r'desktop.ini',
  r'.*\.url',
  r'.*\.lnk'
]

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the files you want to group:\n', process_parent_folder)

def process_parent_folder(root_dir):
  files_to_process = []

  for item in os.listdir(root_dir):
    src = os.path.join(root_dir, item)
    if should_process_item(src):
      group_name = get_group_name(item)
      if group_name:
        output_path = os.path.join(root_dir, group_name)
        if not os.path.exists(output_path):
          os.makedirs(output_path)
        files_to_process.append((src, output_path))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

def should_process_item(item_path):
  if not os.path.isfile(item_path):
    return False

  for pattern in FILE_BLACKLIST:
    if re.fullmatch(pattern, os.path.basename(item_path)):
      return False

  return True

def get_group_name(filename):
  name = re.sub(r'\[[^\]]*\]|\{[^\}]*\}', '', filename)
  if '-' in name:
    name = name[:name.rfind('-')].strip()
  name = os.path.splitext(name)[0].strip()
  name = re.sub(r'\s+', ' ', name)
  return name

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('\nPress Enter to exit...')

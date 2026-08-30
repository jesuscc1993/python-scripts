from concurrent.futures import ThreadPoolExecutor
import os
import sys

from send2trash import send2trash
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm

def main():
  if len(sys.argv) > 2:
    dest_path = sys.argv[1]
    src_path = sys.argv[2]
  else:
    dest_path = Prompt.dir(
      'Delete from path'
    )
    src_path = Prompt.dir(
      '...files that exist on path'
    )

  compare_paths_and_delete_files(src_path, dest_path)
  delete_empty_folders(dest_path)

def compare_paths_and_delete_files(
  src_dir_path: str,
  dest_dir_path: str,
):
  none_deleted = True
  paths_to_delete = []

  for root, _, files in os.walk(src_dir_path):
    for f in files:
      path_a = os.path.join(root, f)
      path_b = path_a.replace(src_dir_path, dest_dir_path, 1)

      if os.path.exists(path_b):
        paths_to_delete.append(path_b)

  if (len(paths_to_delete) > 0):
    with ThreadPoolExecutor() as executor, tqdm(total = len(paths_to_delete), desc = f'Deleting from "{dest_dir_path}"') as progress:
      for _ in executor.map(delete_path, paths_to_delete):
        progress.update(1)

      none_deleted = False

  if none_deleted:
    logger.log('No file matches were found.')
  else:
    logger.success(f'Finished deleting from "{dest_dir_path}" files that already existed in "{src_dir_path}".')

def delete_path(path: str):
  send2trash(path)
  tqdm.write(logger.format_debug(f'Deleted "{path}".'))

def delete_empty_folders(
  parent_folder_path: str,
):
  for root, dirs, _ in os.walk(parent_folder_path, topdown = False):
    for dir_name in dirs:
      try:
        os.rmdir(os.path.join(root, dir_name))
      except OSError:
        pass

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

import os
import sys

from send2trash import send2trash
from mtlogger import logger
from mtprompt import Prompt

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

  for root, _, files in os.walk(src_dir_path):
    for f in files:
      path_a = os.path.join(root, f)
      path_b = path_a.replace(src_dir_path, dest_dir_path, 1)
      if os.path.exists(path_b):
        send2trash(path_b)
        none_deleted = False
        logger.debug(f'Deleted "{path_b}".')

  if none_deleted:
    logger.log('No file matches were found.')
  else:
    logger.success(f'Finished deleting from "{dest_dir_path}" files that already existed in "{src_dir_path}".\n')

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
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

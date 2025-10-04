import os
import sys

from _common import compress_child_folders, select_parent_folder
from mtlogger import logger

def main():
  if len(sys.argv) > 1:
    compress_child_folders(sys.argv[1])
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the subfolders you want to compress:\n',
      process_root_folder
    )

def process_root_folder(parent_folder):
  for root, dirs, _ in os.walk(parent_folder):
    for dir_name in dirs:
      item_path = os.path.join(root, dir_name)
      compress_child_folders(item_path)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

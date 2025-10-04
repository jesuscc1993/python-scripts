import sys

from mtlogger import logger
from _common import compress_child_folders, select_parent_folder

def main():
  if len(sys.argv) > 1:
    compress_child_folders(sys.argv[1])
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the folders you want to compress:\n',
      compress_child_folders
    )

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

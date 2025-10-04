import sys

from _common import extract_child_archives, select_parent_folder
from mtlogger import logger

def main():
  if len(sys.argv) > 1:
    extract_child_archives(sys.argv[1])
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the folders you want to compress:\n',
      extract_child_archives
    )

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

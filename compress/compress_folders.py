import sys
import winsound

from mtlogger import logger
from mtprompt import Prompt

from _common import compress_child_folders, ZIP_TYPES

def main():
  root_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the folders you want to compress:')
  type = sys.argv[2] if len(sys.argv) > 2 else ZIP_TYPES[0]
  depth = int(sys.argv[3]) if len(sys.argv) > 3 else 1

  compress_child_folders(root_dir, type, depth)
  logger.info(f'Successfully compressed folders in "{root_dir}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')

  winsound.MessageBeep()
  Prompt.enterToExit()

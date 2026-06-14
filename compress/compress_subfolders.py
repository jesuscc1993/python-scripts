import sys
import winsound

from mtlogger import logger
from mtprompt import Prompt

from _common import compress_child_folders, ZIP_TYPES

def main():
  parent_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the folders you want to compress')
  type = sys.argv[2] if len(sys.argv) > 2 else ZIP_TYPES[0]
  min_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
  max_depth = int(sys.argv[4]) if len(sys.argv) > 4 else min_depth

  compress_child_folders(parent_dir, type, min_depth, max_depth)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  winsound.MessageBeep()
  Prompt.enter_to_exit()

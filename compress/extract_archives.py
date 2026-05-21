import sys
import winsound

from mtlogger import logger
from mtprompt import Prompt

from _common import extract_child_archives

def main():
  root_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the folders you want to extract:')

  extract_child_archives(root_dir)
  logger.info(f'Successfully extracted archives in "{root_dir}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')

  winsound.MessageBeep()
  Prompt.enterToExit()

import sys
import winsound

from mtlogger import logger
from mtprompt import Prompt

from _common import extract_child_archives

def main():
  parent_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the folders you want to extract:')

  extract_child_archives(parent_dir)
  logger.info(f'Successfully extracted archives in "{parent_dir}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  winsound.MessageBeep()
  Prompt.enterToExit()

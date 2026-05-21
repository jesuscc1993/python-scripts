import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import process_parent_folder, prompt_depth, prompt_path

IMAGE_FILENAMES = ['ICON0.PNG']

def main():
  if len(sys.argv) > 1:
    parent_path = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 1
  else:
    parent_path = prompt_path('Enter the folder path to process:\n')
    depth = prompt_depth()

  process_parent_folder(parent_path, depth, IMAGE_FILENAMES)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enterToExit()

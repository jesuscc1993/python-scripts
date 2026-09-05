import sys

from mtlogger import logger
from mtprompt import Prompt, to_dir, to_int

from _common import process_parent_folder

IMAGE_FILENAMES = ['ICON0.PNG']

def main():
  if len(sys.argv) > 1:
    parent_path = to_dir(sys.argv[1])
    depth = to_int(sys.argv[2]) if len(sys.argv) > 2 else 1
  else:
    parent_path = Prompt.dir(
      'Enter the path to the directory containing the PlayStation saves you want to process'
    )
    depth = Prompt.int(
      'Enter the depth for processing subfolders',
      default=1
    )

  process_parent_folder(parent_path, depth, IMAGE_FILENAMES)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

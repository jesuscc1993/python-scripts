import os
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import rename_items_by_sequential_pattern

def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your files'
    )

  name_pattern = Prompt.str(
    'Enter the name pattern\nUse $ for number interpolation\n',
    default='$'
  )

  items = [
    f
    for f in os.listdir(parent_dir)
    if os.path.isfile(os.path.join(parent_dir, f)) and not f.startswith('.')
  ]
  rename_items_by_sequential_pattern(parent_dir, items, name_pattern)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

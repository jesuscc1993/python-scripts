import os

from mtlogger import logger
from mtprompt import Prompt

from _common import process_items

def main():
  parent_dir = input('Enter the path to the folder containing your folders:\n').strip(' "\'')
  print()

  name_pattern = input('Enter the name pattern pattern (optional; use $ for number interpolation):\n').strip() or '$'
  print()

  items = [f for f in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, f)) and not f.startswith('.')]
  process_items(parent_dir, items, name_pattern)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enter_to_exit()

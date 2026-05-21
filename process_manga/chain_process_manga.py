from mtlogger import logger
from mtprompt import Prompt

from _common import select_parent_folder, run_scripts_in_sequence

SCRIPT_NAMES = [
  'merge_volumes',
  'rename_items',
  'crop_borders',
  '../compress/compress_folders'
]

def process_parent_folder(parent_folder):
  run_scripts_in_sequence(SCRIPT_NAMES, parent_folder)

if __name__ == '__main__':
  try:
    select_parent_folder(None, process_parent_folder)
  except Exception as ex:
    logger.unhandledError(ex)
    Prompt.enterToExit()

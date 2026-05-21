from mtlogger import logger
from mtprompt import Prompt

from _common import select_parent_folder, run_scripts_in_sequence

SCRIPT_NAMES = [
  '../compress/compress_folders'
]

def process_parent_folder(parent_folder):
  run_scripts_in_sequence(SCRIPT_NAMES, parent_folder)

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder containing the folders you want to compress:\n', process_parent_folder)
  except Exception as ex:
    logger.unhandledError(ex)
    Prompt.enterToExit()

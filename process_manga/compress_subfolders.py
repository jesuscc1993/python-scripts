from mtlogger import logger
from mtprompt import Prompt

from _common import select_parent_folder, run_scripts_in_sequence

SCRIPT_NAMES = [
  '../compress/compress_subfolders',
  'rename_items'
]

def process_parent_folder(
  parent_folder_path: str,
):
  run_scripts_in_sequence(SCRIPT_NAMES, parent_folder_path)

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder containing the folders you want to compress:\n', process_parent_folder)
  except Exception as ex:
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

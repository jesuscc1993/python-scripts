from mtlogger import logger
from mtprompt import Prompt

from _common import select_parent_folder, run_scripts_in_sequence

SCRIPT_NAMES = [
  '../compress/extract_archives $dir',
  'prefix_volumes $dir',
  'merge_volumes $dir',
  '../compress/compress_folders $dir ZIP Y',
  'rename_items $dir',
  '../rename/rename_zip_to_cbz $dir'
]

def process_parent_folder(
  parent_folder_path: str,
):
  run_scripts_in_sequence(SCRIPT_NAMES, parent_folder_path)

if __name__ == '__main__':
  try:
    select_parent_folder(None, process_parent_folder)
  except Exception as ex:
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

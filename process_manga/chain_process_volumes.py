import sys

from mtlogger import logger
from mtprompt import Prompt, to_dir

from _common import select_parent_folder, run_scripts_in_sequence

SCRIPT_NAMES = [
  '../compress/extract_archives $dir',
  'prefix_volumes $dir',
  'chain_process_manga $dir',
]


def main():
  if len(sys.argv) > 1:
    process_parent_folder(to_dir(sys.argv[1]))
  else:
    select_parent_folder(None, process_parent_folder)


def process_parent_folder(
  parent_folder_path: str,
):
  run_scripts_in_sequence(SCRIPT_NAMES, parent_folder_path)


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

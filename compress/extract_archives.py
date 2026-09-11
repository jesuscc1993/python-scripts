import sys

from mtlogger import logger
from mtprompt import Prompt, to_dir

from _common import extract_child_archives

def main():
  parent_dir = to_dir(sys.argv[1]) if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the folders you want to extract')

  logger.log(f'Extracting archives in "{parent_dir}"...')
  success = extract_child_archives(parent_dir)

  if success:
    logger.success(f'Extracted archives in "{parent_dir}".')
  else:
    logger.error(f'Failed to extract some archives in "{parent_dir}".')

  return success

if __name__ == '__main__':
  try:
    success = main()
  except Exception as ex:
    logger.unhandled_error(ex)
    success = False

  Prompt.enter_to_exit(timeout=success)

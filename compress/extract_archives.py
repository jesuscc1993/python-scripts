import sys

from mtlogger import logger
from mtprompt import Prompt, to_dir

from _common import extract_child_archives
from _constants import FAILED, INCOMPLETE, SUCCEEDED

def main():
  parent_dir = to_dir(sys.argv[1]) if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the folders you want to extract')

  logger.log(f'Extracting archives in "{parent_dir}"...')
  status = extract_child_archives(parent_dir)

  if status == SUCCEEDED:
    logger.success(f'Extracted archives in "{parent_dir}".')

  elif status == INCOMPLETE:
    logger.warn(f'Extraction did not complete for archives in "{parent_dir}".')

  elif status == FAILED:
    logger.error(f'Failed to extract some archives in "{parent_dir}".')

  return status

if __name__ == '__main__':
  try:
    status = main()
  except Exception as ex:
    logger.unhandled_error(ex)
    status = FAILED

  Prompt.enter_to_exit(timeout=status == SUCCEEDED)

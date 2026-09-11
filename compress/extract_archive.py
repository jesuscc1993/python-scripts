import sys

from mtlogger import logger
from mtprompt import Prompt, to_bool, to_file

from _common import extract_archive

def main():
  archive_path = to_file(sys.argv[1]) if len(sys.argv) > 1 else Prompt.file('Enter the path to the archive you want to extract')
  remove_archive = to_bool(sys.argv[2]) if len(sys.argv) > 2 else True

  logger.log(f'Extracting archive "{archive_path}"...')
  success = extract_archive(archive_path, remove_archive)

  if success:
    logger.success(f'Extracted archive "{archive_path}".')
  else:
    logger.error(f'Failed to extract archive "{archive_path}".')

  return success

if __name__ == '__main__':
  try:
    success = main()
  except Exception as ex:
    logger.unhandled_error(ex)
    success = False

  Prompt.enter_to_exit(timeout=success)
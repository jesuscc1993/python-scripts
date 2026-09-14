import os

from mtlogger import logger
from mtprompt import Prompt

from _common import delete_children_for_dir, delete_children_for_dirs

CRASH_DUMP_DIRS = [
  os.path.expandvars(r'%SystemRoot%\Minidump'),
  os.path.expandvars(r'%SystemRoot%'),
  os.path.expandvars(r'%LocalAppData%\CrashDumps'),
]
CRASH_DUMP_FILE_PATTERNS = ['*.dmp', '*.mdmp']

def main():
  cleanup_temp()
  cleanup_crash_dumps()

def cleanup_temp():
  logger.log('Deleting temporary files...')

  temp_dir = os.getenv('TEMP')
  if not (temp_dir and os.path.exists(temp_dir)):
    logger.warn('Temporary directory not found. Skipping...')
    return

  delete_children_for_dir(temp_dir)

def cleanup_crash_dumps():
  delete_children_for_dirs(CRASH_DUMP_DIRS, CRASH_DUMP_FILE_PATTERNS)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

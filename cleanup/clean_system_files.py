import os
import glob

from mtlogger import logger
from mtprompt import Prompt

from _common import delete_children_by_dir_pattern

def main():
  cleanup_temp()
  cleanup_crash_dumps()

def cleanup_temp():
  logger.log('Deleting temporary files...')

  temp_dir = os.getenv('TEMP')
  if not (temp_dir and os.path.exists(temp_dir)):
    logger.warn('Temporary directory not found. Skipping...')
    return

  delete_children_by_dir_pattern(temp_dir)

def cleanup_crash_dumps():
  logger.log('Deleting crash dump files...')

  directories = [
    os.path.expandvars(r'%SystemRoot%\Minidump'),
    os.path.expandvars(r'%SystemRoot%'),
    os.path.expandvars(r'%LocalAppData%\CrashDumps'),
  ]

  for directory in directories:
    if not os.path.exists(directory):
      logger.warn(f'Directory "{directory}" not found. Skipping...')
      continue

    for ext in ['.dmp', '.mdmp']:
      pattern = os.path.join(directory, f'*{ext}')
      for file_path in glob.glob(pattern):
        try:
          os.remove(file_path)
          logger.debug(f'Deleted "{file_path}"')

        except Exception as ex:
          logger.error(f'Could not delete crash dump file: {ex}')

  logger.success('Finished deleting crash dump files.\n')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

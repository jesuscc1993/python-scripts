import os
import glob
import shutil

from mtlogger import logger
from mtprompt import Prompt

def main():
  cleanup_temp()
  cleanup_crash_dumps()

def cleanup_temp():
  logger.log('Deleting temp files...')

  temp_dir = os.getenv('TEMP')
  if temp_dir and os.path.exists(temp_dir):
    for item in os.listdir(temp_dir):
      try:
        item_path = os.path.join(temp_dir, item)
        if os.path.isfile(item_path):
          os.remove(item_path)
        elif os.path.isdir(item_path):
          shutil.rmtree(item_path, ignore_errors=True)

        logger.debug(f'Deleted "{item_path}"')
      except Exception as ex:
        logger.error(f'Could not delete "{item_path}": {ex}')
        continue

    logger.success('Finished deleting temp files.\n')
  else:
    logger.warn("TEMP directory not found. Skipping...")

def cleanup_crash_dumps():
  logger.log('Deleting crash dump files...')

  directories = [
    os.path.expandvars(r'%SystemRoot%\Minidump'),
    os.path.expandvars(r'%SystemRoot%'),
    os.path.expandvars(r'%LocalAppData%\CrashDumps'),
  ]

  for directory in directories:
    if not os.path.exists(directory):
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
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

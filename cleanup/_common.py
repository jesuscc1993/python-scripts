import ctypes
import glob
import os
import shutil
import sys

from mtlogger import logger

ALL_FILES_PATTERN = '*'

def run_as_admin():
  if os.name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

def delete_children_for_dirs(dir_patterns, file_patterns = [ALL_FILES_PATTERN]):
  for dir_pattern in dir_patterns:
    delete_children_for_dir(dir_pattern, file_patterns)

def delete_children_for_dir(dir_pattern, file_patterns = [ALL_FILES_PATTERN]):
  logger.log(f'Cleaning "{dir_pattern}"...')

  dir_path = os.path.expandvars(dir_pattern)
  matching_dirs = [path for path in glob.glob(dir_path) if os.path.isdir(path)]
  failed = False

  if not matching_dirs:
    logger.warn(f'{dir_pattern} directory not found. Skipping...\n')
    return False

  for matching_dir in matching_dirs:
    try:
      items = [
        item_path
        for file_pattern in file_patterns
        for item_path in glob.glob(os.path.join(matching_dir, file_pattern))
      ]

    except Exception as ex:
      logger.error(f'Could not list "{matching_dir}": {ex}')
      failed = True
      continue

    for item_path in items:
      try:
        if os.path.isfile(item_path):
          os.remove(item_path)
        elif os.path.isdir(item_path):
          shutil.rmtree(item_path)

        logger.debug(f'Deleted "{item_path}"')

      except Exception as ex:
        logger.error(f'Could not delete "{item_path}": {ex}')
        failed = True
        continue

  if failed:
    logger.warn(f'  Finished cleaning "{dir_pattern}" with errors.\n')
  else:
    logger.success(f'Finished cleaning "{dir_pattern}".\n')

  return not failed

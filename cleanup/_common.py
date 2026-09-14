import ctypes
import glob
import os
import shutil
import sys

from mtlogger import logger

def run_as_admin():
  if os.name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

def delete_children_by_dir_patterns(dir_patterns):
  for dir_pattern in dir_patterns:
    delete_children_by_dir_pattern(dir_pattern)

def delete_children_by_dir_pattern(dir_pattern):
  logger.log(f'Cleaning "{dir_pattern}"...')

  dir_path = os.path.expandvars(dir_pattern)
  matching_dirs = [path for path in glob.glob(dir_path) if os.path.isdir(path)]

  if not matching_dirs:
    logger.warn(f'{dir_pattern} directory not found. Skipping...\n')
    return

  for matching_dir in matching_dirs:
    for item in os.listdir(matching_dir):
      try:
        item_path = os.path.join(matching_dir, item)
        if os.path.isfile(item_path):
          os.remove(item_path)
        elif os.path.isdir(item_path):
          shutil.rmtree(item_path, ignore_errors=True)

        logger.debug(f'Deleted "{item_path}"')

      except Exception as ex:
        logger.error(f'Could not delete "{item_path}": {ex}')
        continue

  logger.success(f'Finished cleaning "{dir_pattern}".\n')

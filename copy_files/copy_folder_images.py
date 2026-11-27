import os
import shutil
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import enforce_unique_path
from _constants import SUCCESS_TIMEOUT

FILES_TO_COPY = {'cover.jpg', 'desktop.ini', 'folder.jpg', 'icon.ico'}


def main():
  if len(sys.argv) > 2:
    src_path = sys.argv[1]
    dest_path = sys.argv[2]
  else:
    src_path = Prompt.dir('Enter the path containing the files to copy')
    dest_path = Prompt.dir('Enter the path the files will be copied to')

  try:
    enforce_unique_path(src_path, dest_path)
    copy_folder_assets(src_path, dest_path)
    return True

  except ValueError as ex:
    logger.error(ex)
    return False


def copy_folder_assets(
  src_dir_path: str,
  dest_dir_path: str,
):
  for item in os.listdir(src_dir_path):
    item_path = os.path.join(src_dir_path, item)
    if os.path.isdir(item_path):
      dest_folder = os.path.join(dest_dir_path, item)
      os.makedirs(dest_folder, exist_ok=True)

      for file in os.listdir(item_path):
        if file in FILES_TO_COPY:
          src_file = os.path.join(item_path, file)
          dest_file = os.path.join(dest_folder, file)
          shutil.copy2(src_file, dest_file)
          logger.debug(f'Copied "{src_file}" as "{dest_file}".')

  logger.success(f'Finished copying "{src_dir_path}" to "{dest_dir_path}".')


if __name__ == '__main__':
  try:
    success = main()
  except Exception as ex:
    logger.unhandled_error(ex)
    success = False

  Prompt.enter_to_exit(timeout=SUCCESS_TIMEOUT, success=success)

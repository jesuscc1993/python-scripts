import os
import shutil
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import enforce_unique_path


def main():
  if len(sys.argv) > 2:
    src_dir_path = sys.argv[1]
    dest_dir_path = sys.argv[2]
  else:
    src_dir_path = Prompt.dir('Enter the path containing the files to copy')
    dest_dir_path = Prompt.str('Enter the path the files will be copied to')

  try:
    enforce_unique_path(src_dir_path, dest_dir_path)
    backup_updated_files(src_dir_path, dest_dir_path)
  except ValueError as ex:
    logger.error(ex)


def backup_updated_files(
  src_dir_path: str,
  dest_dir_path: str,
):
  for src_dir, _, files in os.walk(src_dir_path):
    relative_path = os.path.relpath(src_dir, src_dir_path)
    dest_dir = os.path.join(dest_dir_path, relative_path)
    os.makedirs(dest_dir, exist_ok=True)

    for file in files:
      src_file_path = os.path.join(src_dir, file)
      dest_file_path = os.path.join(dest_dir, file)

      if os.path.exists(dest_file_path) and os.path.getmtime(
        src_file_path
      ) <= os.path.getmtime(dest_file_path):
        logger.trace(
          f'Skipping "{src_file_path}". Destination file is up to date.'
        )
        continue

      try:
        shutil.copy2(src_file_path, dest_file_path)
      except Exception as ex:
        logger.error(f'Failed to back up "{src_file_path}":\n{ex}')
        continue

      logger.success(f'Backed up "{src_file_path}" as "{dest_file_path}".')


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

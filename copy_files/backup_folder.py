import os
import shutil
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import enforce_unique_path

def main():
  if len(sys.argv) > 2:
    src_path = sys.argv[1]
    dest_path = sys.argv[2]
  else:
    src_path = Prompt.dir('Enter the path containing the files to copy')
    dest_path = Prompt.str('Enter the path the files will be copied to')

  try:
    enforce_unique_path(src_path, dest_path)
    backup_updated_files(src_path, dest_path)
  except ValueError as ex:
    logger.error(ex)

def backup_updated_files(src_path, dest_path):
  for src_dir, _, files in os.walk(src_path):
    relative_path = os.path.relpath(src_dir, src_path)
    dest_dir = os.path.join(dest_path, relative_path)
    os.makedirs(dest_dir, exist_ok = True)

    for file in files:
      src_file = os.path.join(src_dir, file)
      dest_file = os.path.join(dest_dir, file)

      if not os.path.exists(dest_file) or os.path.getmtime(src_file) > os.path.getmtime(dest_file):
        shutil.copy2(src_file, dest_file)
        logger.success(f'Backed up "{src_file}" as "{dest_file}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

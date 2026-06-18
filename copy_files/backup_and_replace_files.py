import os
import sys
import shutil

from mtlogger import logger
from mtprompt import Prompt

from _common import enforce_unique_path

def main():
  if len(sys.argv) > 2:
    src_path = sys.argv[1]
    dest_path = sys.argv[2]
    matches_only = (sys.argv[3] if len(sys.argv) > 3 else 'n').strip().lower() == 'n'
  else:
    src_path = Prompt.dir(
      'Enter the path containing the files to copy'
    )
    dest_path = Prompt.str(
      'Enter the path the files will be copied to'
    )
    matches_only = Prompt.bool(
      'Matches only?',
      default=True
    )

  try:
    enforce_unique_path(src_path, dest_path)
    rename_and_copy_files(src_path, dest_path, matches_only)
  except ValueError as ex:
    logger.error(ex)

def rename_and_copy_files(src_path, dest_path, matches_only):
  files = os.listdir(src_path)
  if files:
    os.makedirs(dest_path, exist_ok=True)

    for filename in files:
      src_file = os.path.join(src_path, filename)
      dest_file = os.path.join(dest_path, filename)
      if os.path.isfile(src_file) and (os.path.exists(dest_file) or not matches_only):
        backup_file(dest_file)
        shutil.copy(src_file, dest_file)
    logger.success(f'Finished copying files from "{src_path}" to "{dest_path}".')

def backup_file(file_path):
  if os.path.isfile(file_path):
    name, ext = os.path.splitext(file_path)
    new_filename = f'{name}.bak{ext}'
    bak_path = os.path.join(os.path.dirname(file_path), new_filename)

    if not os.path.isfile(bak_path):
      os.rename(file_path, bak_path)
      logger.debug(f'Backed up "{file_path}" as "{bak_path}".')
    else:
      logger.trace(f'Backup file "{bak_path}" already exists and will be reused.')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

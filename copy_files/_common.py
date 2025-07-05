import os
import shutil
import sys

from datetime import datetime

BACKUP_EXT = '.bak'
BACKUP_PATH = 'backups'
TIMESTAMP_FORMAT = '%Y-%m-%d_%H-%M-%S'

def prompt_path(prompt_message, optional = False):
  path = input(prompt_message).strip(' "\'')
  if not path or not os.path.isdir(path):
    print(f'The specified path "{path}" is not a directory.')
    if not optional: sys.exit(1)
    return None
  print('')
  return path

def prompt_file(prompt_message, optional = False):
  file_path = input(prompt_message).strip(' "\'')
  if not file_path or not os.path.isfile(file_path):
    print(f'The specified file "{file_path}" does not exist.')
    if not optional:
      sys.exit(1)
    return None
  print('')
  return file_path

def rename_with_timestamp(dir_path, src_file_path):
  file_name = os.path.basename(src_file_path)

  if os.path.exists(src_file_path):
    mtime = os.path.getmtime(src_file_path)
    timestamp = datetime.fromtimestamp(mtime).strftime(TIMESTAMP_FORMAT)
    file_stem, file_ext = os.path.splitext(file_name)
    stamped_file_name = f'{file_stem.replace(BACKUP_EXT, '')}.{timestamp}{file_ext}'
    stamped_file_path = os.path.join(dir_path, stamped_file_name)
    shutil.move(src_file_path, stamped_file_path)
    print(f'Backup up existing {file_name} as {stamped_file_name}')

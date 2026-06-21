import os
import shutil

from datetime import datetime
from mtlogger import logger

BACKUP_EXT = '.bak'
BACKUP_PATH = 'backups'
TIMESTAMP_FORMAT = '%Y-%m-%d_%H-%M-%S'
WATCH_INTERVAL = 60

def rename_with_timestamp(dir_path: str, src_file_path: str):
  file_name = os.path.basename(src_file_path)

  if os.path.exists(src_file_path):
    mtime = os.path.getmtime(src_file_path)
    timestamp = datetime.fromtimestamp(mtime).strftime(TIMESTAMP_FORMAT)
    file_stem, file_ext = os.path.splitext(file_name)
    stamped_file_name = f'{file_stem.replace(BACKUP_EXT, '')}.{timestamp}{file_ext}'
    stamped_file_path = os.path.join(dir_path, stamped_file_name)
    shutil.move(src_file_path, stamped_file_path)
    logger.success(f'Backed up existing "{file_name}" as "{stamped_file_name}"')

def enforce_unique_path(pathA: str, pathB: str):
  if pathA == pathB:
    raise ValueError('Source and destination paths cannot be the same.')

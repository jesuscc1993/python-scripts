import os

from mtattr import Attr
from mtlogger import logger

DIR_BLACKLIST = ['__InstallData__']
EXCLUSION_FILE = '.noscan'

def scan_dir_names(
  dir_paths: list[str],
):
  return [
    entry.name
    for dir_path in dir_paths
    for entry in os.scandir(dir_path)
    if entry.is_dir() and not should_skip_dir(entry.path)
  ]

def should_skip_dir(
  dir_path: str,
):
  if Attr.is_hidden(dir_path):
    logger.trace(f'  Skipping "{dir_path}". Directory is hidden.')
    return True

  if has_exclusion_file(dir_path):
    logger.trace(f'  Skipping "{dir_path}". Directory contains a {EXCLUSION_FILE} file.')
    return True

  if os.path.basename(dir_path) in DIR_BLACKLIST:
    logger.trace(f'  Skipping "{dir_path}". Directory is blacklisted.')
    return True

  return False

def has_exclusion_file(
  path: str,
):
  return os.path.exists(os.path.join(path, EXCLUSION_FILE))

def seconds_to_hours(
  seconds: int,
):
  return round(seconds / 1800) / 2 if seconds is not None else None


import ctypes
import os
import shutil
import sys

from mtlogger import logger
from pathlib import Path
from typing import Optional

def make_link(dest: str, src: str, target_is_directory: bool, make_dirs: Optional[bool] = True) -> bool:
  if not Path(src).exists():
    logger.error(f'Source "{src}" does not exist.')
    return

  try:
    remove_link(dest)
  except Exception as ex:
    logger.error(f'Failed to remove existing path "{dest}": {ex}')
    return

  if make_dirs:
    os.makedirs(os.path.dirname(dest), exist_ok=True)

  try:
    Path(dest).symlink_to(src, target_is_directory)
    logger.success(f'Linked "{dest}" to "{src}".')
  except Exception as ex:
    logger.error(f'Failed to link "{dest}" to "{src}": {ex}')

def remove_link(location: str) -> None:
  path = Path(location)
  if path.is_symlink():
    path.unlink(missing_ok=True)
  elif path.exists():
    if path.is_dir() and not any(path.iterdir()):
      path.rmdir()
    else:
      new_location = location + '.bak'
      shutil.move(location, new_location)
      logger.debug(f'  Backed up existing "{location}" as "{new_location}".')

def link_dir(dest: str, src: str, make_dirs: Optional[bool] = True) -> bool:
  return make_link(dest, src, target_is_directory=True, make_dirs=make_dirs)

def link_file(target: str, source: str, make_dirs: Optional[bool] = True) -> bool:
  return make_link(target, source, target_is_directory=False, make_dirs=make_dirs)

def run_as_admin():
  if os.name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

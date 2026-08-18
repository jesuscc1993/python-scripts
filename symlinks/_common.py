
import ctypes
import os
import shutil
import sys

from mtlogger import logger
from pathlib import Path

def make_link(
  dest: str,
  src: str,
  target_is_dir: bool,
  make_dirs = True,
):
  dest_path = os.path.expandvars(dest)
  src_path = os.path.expandvars(src)

  if not Path(src_path).exists():
    logger.error(f'Source "{src_path}" does not exist.')
    return

  try:
    remove_link(dest_path)
  except Exception as ex:
    logger.error(f'Failed to remove existing path "{dest_path}": {ex}')
    return

  dest_dir = os.path.dirname(dest_path)
  if make_dirs:
    os.makedirs(dest_dir, exist_ok=True)
  elif not os.path.isdir(dest_dir):
    logger.warn(f'  Skipping "{dest_dir}". Destination does not exist.')
    return

  try:
    Path(dest_path).symlink_to(src_path, target_is_dir)
    logger.success(f'Linked "{dest_path}" to "{src_path}".')
  except Exception as ex:
    logger.error(f'Failed to link "{dest_path}" to "{src_path}": {ex}')

def remove_link(
  location: str,
):
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

def link_dir(
  dest: str,
  src: str,
  make_dirs = True,
):
  return make_link(dest, src, target_is_dir=True, make_dirs=make_dirs)

def link_file(
  target: str,
  source: str,
  make_dirs = True,
):
  return make_link(target, source, target_is_dir=False, make_dirs=make_dirs)

def run_as_admin():
  if os.name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)



import ctypes
import os

from _common import make_link, run_as_admin

from mtlogger import logger
from mtprompt import Prompt

FILE_ATTRIBUTE_HIDDEN = 0x02

def main():
  while src_path := Prompt.path('Enter the path you want to create a hidden symlink for', optional=True):
    process_dir(src_path)

def process_dir(
  src_path: str,
):
  new_name = os.path.basename(Prompt.str('Enter the new name for the item'))

  parent_dir = os.path.dirname(src_path)
  dest_path = os.path.join(parent_dir, new_name)

  os.rename(src_path, dest_path)
  logger.success(f'Renamed "{src_path}" to "{dest_path}".')

  is_dir = os.path.isdir(dest_path)
  make_link(src_path, dest_path, is_dir, make_dirs=False)
  hide_path(src_path)

  logger.hr()

def hide_path(
  path: str,
):
  ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)

if __name__ == '__main__':
  try:
    run_as_admin()
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit(timeout = True)

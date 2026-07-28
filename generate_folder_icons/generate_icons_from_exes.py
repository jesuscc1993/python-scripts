import os
import re
import sys
import winsound

from mtlogger import logger
from mtprompt import Prompt

from _common import set_folder_icon

ENCODING = 'utf-8'
ICON_KEY = 'IconResource'
INI_FILENAME = 'desktop.ini'
SHELL_SECTION = '.ShellClassInfo'

EXE_EXCLUSION_PATTERNS = [
  r'CrashHandler',
  r'EOSBootstrapper',
  r'Handler',
  r'ModManager',
  r'Setup',
  r'Unins',
  r'Updat'
]

def main():
  if len(sys.argv) > 1:
    parent_path = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 1
  else:
    parent_path = Prompt.dir(
      'Enter the path to the directory containing the exes you want to process'
    )
    depth = Prompt.int(
      'Enter the depth for processing subfolders',
      default=1
    )

  parent_path = os.path.abspath(parent_path)
  parent_depth = parent_path.rstrip(os.sep).count(os.sep)

  process_dir(parent_path)

  for root, dirs, _ in os.walk(parent_path):
    current_depth = root.rstrip(os.sep).count(os.sep) - parent_depth
    if current_depth >= depth:
      dirs.clear()
      continue

    for dir_name in dirs:
      child_path = os.path.join(root, dir_name)
      process_dir(child_path)

  winsound.MessageBeep()
  logger.success(f'Finished setting icons for "{parent_path}".', prefix_newline=True)

def process_dir(dir_path):
  try:
    abs_exe_path = find_exe(dir_path)
    if not abs_exe_path:
      return

    rel_exe_path = os.path.relpath(abs_exe_path, dir_path)
    set_folder_icon(dir_path, rel_exe_path)

  except Exception as ex:
    logger.error(f'Could not process "{dir_path}": {ex}')

def find_exe(dir_path):
  pattern = re.compile('|'.join(EXE_EXCLUSION_PATTERNS), re.IGNORECASE)

  for dirpath, _, filenames in os.walk(dir_path):
    for f in filenames:
      if f.lower().endswith('.exe') and not pattern.search(f):
        return os.path.join(dirpath, f)
  return None

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit(timeout=True)

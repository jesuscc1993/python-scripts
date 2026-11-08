import mtsound
import os
import re
import sys

from mtlogger import logger
from mtprompt import Prompt
from mtvalidation import to_dir, to_int

from _common import set_folder_icon

ENCODING = 'utf-8'
ICON_KEY = 'IconResource'
INI_FILENAME = 'desktop.ini'
SHELL_SECTION = '.ShellClassInfo'

EXE_EXCLUSION_PATTERNS = [
  r'bootstrapper',
  r'bssndrpt',
  r'handler',
  r'manager',
  r'setup',
  r'trainer',
  r'unins',
  r'updat',
  r'upload',
]


def main():
  if len(sys.argv) > 1:
    parent_path = to_dir(sys.argv[1])
    depth = to_int(sys.argv[2]) if len(sys.argv) > 2 else 1
  else:
    parent_path = Prompt.dir(
      'Enter the path to the directory containing the exes you want to process'
    )
    depth = Prompt.int('Enter the depth for processing subfolders', default=1)

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

  mtsound.notify()
  logger.success(
    f'Finished setting icons for "{parent_path}".', prefix_newline=True
  )


def process_dir(
  dir_path: str,
):
  try:
    abs_exe_path = find_exe(dir_path)
    if not abs_exe_path:
      return

    rel_exe_path = os.path.relpath(abs_exe_path, dir_path)
    set_folder_icon(dir_path, rel_exe_path)

  except Exception as ex:
    logger.error(f'Could not process "{dir_path}": {ex}')


def find_exe(
  dir_path: str,
):
  pattern = re.compile('|'.join(EXE_EXCLUSION_PATTERNS), re.IGNORECASE)
  exes = []

  for root, _, file_names in os.walk(dir_path):
    for file_name in file_names:
      if file_name.lower().endswith('.exe') and not pattern.search(file_name):
        exes.append(os.path.join(root, file_name))

  exes.sort(
    key=lambda exe_a: (
      -sum(compare_exes(exe_b, exe_a) for exe_b in exes if exe_b != exe_a),
      len(os.path.basename(exe_a)),
    )
  )

  return exes[0] if exes else None


def compare_exes(
  exe_a: str,
  exe_b: str,
):
  return (
    os.path.splitext(os.path.basename(exe_a))[0]
    .lower()
    .startswith(os.path.splitext(os.path.basename(exe_b))[0].lower())
  )


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

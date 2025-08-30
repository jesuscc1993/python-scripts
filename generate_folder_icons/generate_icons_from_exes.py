import configparser
import os
import re
import sys

from _common import prompt_depth, prompt_path
from _sound_utils import play_notification_sound

ENCODING = 'utf-8'
ICON_KEY = 'IconResource'
INI_FILENAME = 'desktop.ini'
SHELL_SECTION = '.ShellClassInfo'

EXE_EXCLUSION_PATTERNS = [r'unins.*', r'CrashHandler.*', r'EOSBootstrapper.*']

def main():
  if len(sys.argv) > 1:
    parent_path = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 1
  else:
    parent_path = prompt_path('Enter the folder path to process:\n')
    depth = prompt_depth()

  parent_path = os.path.abspath(parent_path)
  parent_depth = parent_path.rstrip(os.sep).count(os.sep)

  for root, dirs, _ in os.walk(parent_path):
    current_depth = root.rstrip(os.sep).count(os.sep) - parent_depth
    if current_depth >= depth:
      dirs.clear()
      continue

    for dir_name in dirs:
      try:
        child_path = os.path.join(root, dir_name)
        if not os.path.isdir(child_path):
          continue

        exe_path = find_exe(child_path)
        if not exe_path:
          continue

        save_icon_to_ini(child_path, exe_path)

      except Exception as e:
        print(f'[ERROR] Could not process "{child_path}": {e}')
        continue

  play_notification_sound()
  print(f'[LOG] Finished setting icons for "{parent_path}".')

def find_exe(folder):
  pattern = re.compile('|'.join(EXE_EXCLUSION_PATTERNS), re.IGNORECASE)

  for dirpath, _, filenames in os.walk(folder):
    for f in filenames:
      if f.lower().endswith('.exe') and not pattern.match(f):
        return os.path.join(dirpath, f)
  return None

def save_icon_to_ini(dir_path, exe_path):
  ini_path = os.path.join(dir_path, INI_FILENAME)

  config = configparser.ConfigParser()
  config.optionxform = str

  if os.path.exists(ini_path):
    config.read(ini_path, encoding = ENCODING)

  if SHELL_SECTION not in config:
    config[SHELL_SECTION] = {}

  if ICON_KEY in config[SHELL_SECTION] and config[SHELL_SECTION][ICON_KEY].strip():
    print(f'[DEBUG] Icon already set for "{dir_path}". Skipping...')
    return

  relative_exe_path = os.path.relpath(exe_path, dir_path)
  config[SHELL_SECTION][ICON_KEY] = f'{relative_exe_path},0'

  with open(ini_path, 'w', encoding = ENCODING) as ini:
    config.write(ini)
    print(f'[DEBUG] Set icon for {dir_path}.')

  os.system(f'attrib +h "{ini_path}"')
  os.system(f'attrib +s +r "{dir_path}"')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

import configparser
import os
import sys

from _common import prompt_path

ENCODING = 'utf-8'
ICON_KEY = 'IconResource'
INI_FILENAME = 'desktop.ini'
SHELL_SECTION = '.ShellClassInfo'

def main():
  if len(sys.argv) > 1:
    parent_path = sys.argv[1]
  else:
    parent_path = prompt_path('Enter the folder path to process:\n')

  for child_dir in os.listdir(parent_path):
    try:
      child_path = os.path.join(parent_path, child_dir)
      if not os.path.isdir(child_path):
        continue

      exe_path = find_exe(child_path)
      if not exe_path:
        continue

      save_icon_to_ini(child_path, exe_path)

    except Exception as e:
      print(f'[ERROR] Could not process "{child_path}": {e}')
      continue

def find_exe(folder):
  for dirpath, _, filenames in os.walk(folder):
    for f in filenames:
      if f.lower().endswith('.exe') and 'unins' not in f.lower():
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

  config[SHELL_SECTION][ICON_KEY] = f'{exe_path},0'

  with open(ini_path, 'w', encoding = ENCODING) as ini:
    config.write(ini)
    print(f'[DEBUG] Saved icon for {dir_path}.')

  os.system(f'attrib +h "{ini_path}"')
  os.system(f'attrib +s +r "{dir_path}"')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

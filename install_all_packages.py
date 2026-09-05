import os
import subprocess

from mtprompt import Prompt

SETUP_FILE = 'setup.py'

def main():
  for path, _, files in os.walk('.'):
    if SETUP_FILE in files:
      subprocess.run(['pip', 'install', path])

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'Unhandled error:  {ex}')

  Prompt.enter_to_exit()

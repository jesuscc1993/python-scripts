import os
import subprocess

from mtprompt import Prompt

REQUIREMENTS_FILE = 'requirements.txt'

def main():
  for path, _, files in os.walk('.'):
    if REQUIREMENTS_FILE in files:
      req_path = os.path.join(path, REQUIREMENTS_FILE)
      print(f'\nInstalling {req_path}...')
      subprocess.run(['pip', 'install', '-r', req_path])

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'Unhandled error:  {ex}')

  Prompt.enter_to_exit()

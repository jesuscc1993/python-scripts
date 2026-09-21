import os
import subprocess

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

  input('\nPress Enter to exit...')

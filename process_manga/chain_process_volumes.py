import os
import subprocess

from _common import exit_with_prompt, print_error, select_parent_folder

SCRIPT_NAMES = [
  '../compress/extract_archives',
  'prefix_volumes',
  'merge_volumes',
  '../compress/compress_folders'
]
def process_parent_folder(parent_folder):
  for script in SCRIPT_NAMES:
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), script + '.py'))

    print(f'\nRunning {script}:')
    subprocess.run(['python', abs_path, parent_folder])

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder you want to process:\n', process_parent_folder)
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()

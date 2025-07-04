import importlib.util
import os
import sys

from _common import exit_with_prompt, print_error, select_parent_folder

SCRIPT_NAMES = ['merge_volumes', 'rename_items', 'crop_borders']

def process_parent_folder(parent_folder):

  for script in SCRIPT_NAMES:
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), script + '.py'))
    sys.argv = [abs_path, parent_folder]

    spec = importlib.util.spec_from_file_location(script, abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    print(f'\nRunning {script}:')
    module.main()

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder you want to process:\n', process_parent_folder)
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()

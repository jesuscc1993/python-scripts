from _common import exit_with_prompt, print_error, select_parent_folder, run_scripts_in_sequence

SCRIPT_NAMES = [
  'merge_volumes',
  'rename_items',
  'crop_borders',
  '../compress/compress_folders'
]

def process_parent_folder(parent_folder):
  run_scripts_in_sequence(SCRIPT_NAMES, parent_folder)

if __name__ == '__main__':
  try:
    select_parent_folder(None, process_parent_folder)
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()

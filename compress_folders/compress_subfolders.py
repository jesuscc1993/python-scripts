import os

from _common import process_parent_folder, select_parent_folder

def process_root_folder(parent_folder):
  for root, dirs, _ in os.walk(parent_folder):
    for dir_name in dirs:
      item_path = os.path.join(root, dir_name)
      process_parent_folder(item_path)

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder containing the folders you want to compress:\n', process_root_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

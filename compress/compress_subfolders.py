import os
import sys

from _common import process_parent_folder, select_parent_folder

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the subfolders you want to compress:\n', process_root_folder)

def process_root_folder(parent_folder):
  for root, dirs, _ in os.walk(parent_folder):
    for dir_name in dirs:
      item_path = os.path.join(root, dir_name)
      process_parent_folder(item_path)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

import os

from tqdm import tqdm

from _sound_utils import play_notification_sound
from _common import process_parent_folder

def main():
  root_folder = input('Enter the path to the parent folder containing the folders you want to compress:\n').strip('" ')
  if not root_folder:
    return
  if not os.path.isdir(root_folder):
    print(f'The specified path "{root_folder}" is not a directory.')
  else:
    process_root_folder(root_folder)
    play_notification_sound()
    print(f'Finished processing "{root_folder}".\n')
  main()

def process_root_folder(parent_folder):
  for root, dirs, _ in os.walk(parent_folder):
    for dir_name in dirs:
      item_path = os.path.join(root, dir_name)
      process_parent_folder(item_path)

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

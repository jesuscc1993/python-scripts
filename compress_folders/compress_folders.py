import os

from tqdm import tqdm

from _sound_utils import play_notification_sound
from _common import process_parent_folder

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders you want to compress:\n').strip('" ')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    process_parent_folder(parent_folder)
    play_notification_sound()
    print(f'Finished processing "{parent_folder}".\n')
  main()

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

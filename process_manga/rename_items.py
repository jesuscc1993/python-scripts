import os
import re
import sys

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _sound_utils import play_notification_sound

def prompt_parent_folder(default_folder = None):
  parent_folder = default_folder or input('Enter the path to the image you want to generate the palette for:\n')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    process_parent_folder(parent_folder)
    play_notification_sound()

def process_parent_folder(parent_folder):
  for root, dirs, files in os.walk(parent_folder, topdown = False):
    all_items = files + dirs

    with ThreadPoolExecutor() as executor:
      list(tqdm(executor.map(lambda item: process_item(root, item), all_items), total = len(all_items), desc=f'Processing "{root}"'))

def process_item(root, item_name):
  new_name = get_processed_name(item_name)
  if item_name != new_name:
    old_path = os.path.join(root, item_name)
    new_path = os.path.join(root, new_name)
    os.rename(old_path, new_path)

def get_processed_name(name):
  new_name = re.sub(r'\s+', ' ', name)
  new_name = re.sub(r'\bchapter\b\s*', 'Ch.', new_name, flags = re.IGNORECASE)
  new_name = re.sub(r'\bvolume\b\s*', 'Vol.', new_name, flags = re.IGNORECASE)
  return new_name

if __name__ == '__main__':
  try:
    parent_folder = sys.argv[1] if len(sys.argv) > 1 else None
    prompt_parent_folder(parent_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('Press Enter to exit...')
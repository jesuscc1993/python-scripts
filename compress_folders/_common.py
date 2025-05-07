import os
import shutil
import zipfile

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _settings import OUTPUT_EXTENSION
from _sound_utils import play_notification_sound

def select_parent_folder(prompt, callback):
  parent_folder = input(prompt).strip('" ')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    callback(parent_folder)
    play_notification_sound()
    print(f'Finished processing "{parent_folder}".\n')
  select_parent_folder(prompt, callback)

def process_parent_folder(parent_folder):
  folders = []
  for root, dirs, _ in os.walk(parent_folder):
    for dir_name in dirs:
      folders.append(os.path.join(root, dir_name))

  with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(process_folder, folders), total=len(folders), desc=f'Processing "{parent_folder}"'))

def process_folder(folder_path):
  folder_name = os.path.basename(folder_path)
  compressed_file_path = f'{folder_path}.{OUTPUT_EXTENSION}'

  if os.path.exists(compressed_file_path):
    print(f'Skipping "{folder_name}". A compressed file with the same name already exists.')
    return

  try:
    with zipfile.ZipFile(compressed_file_path, 'w', zipfile.ZIP_DEFLATED) as compressed_file:
      for root, _, files in os.walk(folder_path):
        for file in files:
          file_path = os.path.join(root, file)
          compressed_file.write(file_path, os.path.relpath(file_path, folder_path))

    shutil.rmtree(folder_path)

  except Exception as e:
    print(f'An error occurred while processing "{folder_name}": {e}')
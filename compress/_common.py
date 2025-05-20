import os
import shutil
import zipfile

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _settings import FOLDER_OUTPUT_EXTENSION
from _sound_utils import play_notification_sound

def select_parent_folder(prompt, callback):
  parent_folder = input(prompt).strip(' "\'')
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

  if len(folders) > 0:
    tmp_dir = os.path.join(parent_folder, '.tmp')
    shutil.rmtree(tmp_dir, ignore_errors = True)
    os.makedirs(tmp_dir)

    with ThreadPoolExecutor() as executor:
      list(tqdm(executor.map(process_folder, folders), total = len(folders), desc = f'Processing "{parent_folder}"'))

    shutil.rmtree(tmp_dir, ignore_errors = True)

def process_folder(folder_path):
  folder_name = os.path.basename(folder_path)
  tmp_dir = os.path.join(os.path.dirname(folder_path), '.tmp')

  zip_filename = f'{folder_name}.{FOLDER_OUTPUT_EXTENSION}'
  tmp_zip_path = os.path.join(tmp_dir, zip_filename)
  final_zip_path = os.path.join(os.path.dirname(folder_path), zip_filename)

  if os.path.exists(final_zip_path):
    print(f'Skipping "{folder_path}". A compressed file with the same name already exists.')
    return

  try:
    files = []
    for root, _, filenames in os.walk(folder_path):
      for file in filenames:
        files.append(os.path.join(root, file))

    if len(files) > 0:
      with zipfile.ZipFile(tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as compressed_file:
        for file_path in files:
          compressed_file.write(file_path, os.path.relpath(file_path, folder_path))

      shutil.move(tmp_zip_path, final_zip_path)
      shutil.rmtree(folder_path)

  except Exception as e:
    print(f'An error occurred while processing "{folder_name}": {e}')
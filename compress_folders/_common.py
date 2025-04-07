import os
import shutil
import zipfile

from tqdm import tqdm

from _settings import OUTPUT_EXTENSION

def process_parent_folder(parent_folder):
  for root, dirs, _ in os.walk(parent_folder):
    for dir_name in dirs:
      item_path = os.path.join(root, dir_name)
      process_folder(item_path)

def process_folder(folder_path):
  folder_name = os.path.basename(folder_path)
  compressed_file_path = f'{folder_path}.{OUTPUT_EXTENSION}'

  if os.path.exists(compressed_file_path):
    print(f'Skipping "{folder_name}". A compressed file with the same name already exists.')
    return

  try:
    with zipfile.ZipFile(compressed_file_path, 'w', zipfile.ZIP_DEFLATED) as compressed_file:
      for root, _, files in os.walk(folder_path):
        for file in tqdm(files, desc=f'Processing "{folder_name}"'):
          file_path = os.path.join(root, file)
          compressed_file.write(file_path, os.path.relpath(file_path, folder_path))

    shutil.rmtree(folder_path)

  except Exception as e:
    print(f'An error occurred while processing "{folder_name}": {e}')
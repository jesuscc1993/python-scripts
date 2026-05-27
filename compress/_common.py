import os
import shutil
import subprocess
import zipfile

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

BAK_TYPE = 'BAK'
ZIP_TYPES = ['ZIP', 'CBZ']

BAK_EXTENSION = f'.{BAK_TYPE.lower()}'

def compress_child_folders(parent_folder, output_type = ZIP_TYPES[0], depth = 1):
  if depth < 1:
    logger.error('Depth must be 1 or greater.')
    return

  folders = []
  for root, dirs, _ in os.walk(parent_folder, topdown = False):
    for dir_name in dirs:
      if dir_name == '.tmp':
        continue

      folder_path = os.path.join(root, dir_name)
      rel_path = os.path.relpath(folder_path, parent_folder)
      current_depth = rel_path.count(os.sep) + 1

      if current_depth == depth:
        folders.append(folder_path)

  if len(folders) > 0:
    tmp_dir = os.path.join(parent_folder, '.tmp')
    os.makedirs(tmp_dir, exist_ok = True)
    subprocess.call(['attrib', '+H', str(tmp_dir)])

    try:
      with ThreadPoolExecutor() as executor:
        list(tqdm(
          executor.map(lambda folder: compress_folder(folder, output_type), folders),
          total = len(folders),
          desc = f'Processing "{parent_folder}"'
        ))
    finally:
      shutil.rmtree(tmp_dir, ignore_errors = True)

def compress_folder(folder_path, output_type):
  folder_name = os.path.basename(folder_path)

  parent_dir = os.path.dirname(folder_path)
  tmp_dir = os.path.join(parent_dir, '.tmp')

  zip_filename = f'{folder_name}.{output_type.lower()}'
  tmp_zip_path = os.path.join(tmp_dir, zip_filename)
  final_zip_path = os.path.join(parent_dir, zip_filename)

  if os.path.exists(final_zip_path):
    logger.dim(f'Skipping "{folder_path}". A compressed file with the same name already exists.')
    return

  try:
    files = []
    for root, _, filenames in os.walk(folder_path, topdown = False):
      for file in filenames:
        files.append(os.path.join(root, file))

    if len(files) > 0:
      with zipfile.ZipFile(tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as compressed_file:
        for file_path in files:
          compressed_file.write(file_path, os.path.relpath(file_path, folder_path))

      shutil.move(tmp_zip_path, final_zip_path)
      shutil.rmtree(folder_path)

  except Exception as ex:
    logger.error(f'An error occurred while processing "{folder_name}":\n{ex}')

def extract_child_archives(parent_folder):
  archives = []
  for root, _, files in os.walk(parent_folder, topdown = False):
    for file_name in files:
      if any(file_name.upper().endswith(f'.{ext}') for ext in ZIP_TYPES):
        archives.append(os.path.join(root, file_name))

  for archive_path in tqdm(archives, desc=f'Processing "{parent_folder}"'):
    extract_archive(archive_path)

def extract_archive(archive_path):
  folder_name = os.path.splitext(os.path.basename(archive_path))[0]
  target_dir = os.path.join(os.path.dirname(archive_path), folder_name)

  if os.path.exists(target_dir):
    logger.dim(f'Skipping "{archive_path}". Folder exists.')
    return

  with zipfile.ZipFile(archive_path, 'r') as compressed_file:
    compressed_file.extractall(target_dir)

  os.remove(archive_path)

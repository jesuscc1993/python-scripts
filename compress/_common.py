import os
import shutil
import subprocess
import zipfile

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

from _sound_utils import play_notification_sound

ZIP_EXTENSIONS = ['ZIP', 'CBR', 'CBZ']

def select_parent_folder(prompt, callback):
  parent_folder = input(prompt).strip(' "\'')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    logger.error(f'The specified path "{parent_folder}" is not a directory.')
  else:
    callback(parent_folder)
    play_notification_sound()
    logger.log(f'Finished processing "{parent_folder}".\n')
  select_parent_folder(prompt, callback)

def compress_child_folders(parent_folder, output_extension = ZIP_EXTENSIONS[0]):
  folders = []
  for root, dirs, _ in os.walk(parent_folder, topdown = False):
    for dir_name in dirs:
      if dir_name != '.tmp':
        folders.append(os.path.join(root, dir_name))

  if len(folders) > 0:
    tmp_dir = os.path.join(parent_folder, '.tmp')
    shutil.rmtree(tmp_dir, ignore_errors = True)
    os.makedirs(tmp_dir)
    subprocess.call(['attrib', '+H', str(tmp_dir)])

    with ThreadPoolExecutor() as executor:
      list(tqdm(
        executor.map(lambda folder: compress_folder(folder, output_extension), folders),
        total = len(folders), desc = f'Processing "{parent_folder}"'
      ))

    shutil.rmtree(tmp_dir, ignore_errors = True)

def compress_folder(folder_path, output_extension = ZIP_EXTENSIONS[0]):
  folder_name = os.path.basename(folder_path)
  tmp_dir = os.path.join(os.path.dirname(folder_path), '.tmp')

  zip_filename = f'{folder_name}.{output_extension.lower()}'
  tmp_zip_path = os.path.join(tmp_dir, zip_filename)
  final_zip_path = os.path.join(os.path.dirname(folder_path), zip_filename)

  if os.path.exists(final_zip_path):
    logger.debug(f'Skipping "{folder_path}". A compressed file with the same name already exists.')
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
    logger.error(f'An error occurred while processing "{folder_name}": {ex}')

def extract_child_archives(parent_folder):
  archives = []
  for root, _, files in os.walk(parent_folder, topdown = False):
    for file_name in files:
      if any(file_name.upper().endswith(f'.{ext}') for ext in ZIP_EXTENSIONS):
        archives.append(os.path.join(root, file_name))

  for archive_path in tqdm(archives, desc=f'Processing "{parent_folder}"'):
    extract_archive(archive_path)

def extract_archive(archive_path):
  folder_name = os.path.splitext(os.path.basename(archive_path))[0]
  target_dir = os.path.join(os.path.dirname(archive_path), folder_name)

  if os.path.exists(target_dir):
    logger.debug(f'Skipping "{archive_path}". Folder exists.')
    return

  with zipfile.ZipFile(archive_path, 'r') as compressed_file:
    compressed_file.extractall(target_dir)

  os.remove(archive_path)
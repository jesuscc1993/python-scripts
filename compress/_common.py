import os
import re
import shutil
import tempfile
import zipfile

from concurrent.futures import ThreadPoolExecutor
from fnmatch import fnmatch
from mtlogger import logger
from tqdm import tqdm

BAK_TYPE = 'BAK'
ZIP_TYPES = ['ZIP', 'CBZ']

BAK_EXTENSION = f'.{BAK_TYPE.lower()}'

def compress_child_folders(
  parent_folder_path: str,
  output_type: str,
  remove_original = False,
  min_depth = 1,
  max_depth = 1,
):
  logger.log(f'Compressing folders in "{parent_folder_path}"...')

  if max_depth < 1:
    logger.error('Depth must be 1 or greater.')
    return

  folders = []
  for root, dirs, _ in os.walk(parent_folder_path, topdown = False):
    for dir_name in dirs:
      folder_path = os.path.join(root, dir_name)
      rel_folder_path = os.path.relpath(folder_path, parent_folder_path)
      current_depth = rel_folder_path.count(os.sep) + 1

      if min_depth <= current_depth <= max_depth:
        folders.append(folder_path)

  if folders:
    with ThreadPoolExecutor() as executor:
      list(tqdm(
        executor.map(lambda folder: compress_folder(folder, output_type, remove_original), folders),
        total = len(folders),
        desc = f'Processing "{parent_folder_path}"'
      ))

    logger.success(f'Finished compressing folders in "{parent_folder_path}".')
  else:
    logger.warn(f'No folders found in "{parent_folder_path}".')

def compress_folder(
  folder_path: str,
  output_type: str = ZIP_TYPES[0],
  remove_original = False,
  exclusion_patterns: list = None,
):
  folder_name = os.path.basename(folder_path)
  parent_dir = os.path.dirname(folder_path)

  zip_filename = f'{folder_name}.{output_type.lower()}'
  tmp_name = re.sub(r'[<>:"/\\|?*]', '_', folder_path)
  tmp_zip_path = os.path.join(tempfile.gettempdir(), f'{tmp_name}.tmp')
  final_zip_path = os.path.join(parent_dir, zip_filename)

  if os.path.exists(final_zip_path):
    logger.trace(f'Skipping "{folder_path}". A compressed file with the same name already exists.')
    return

  try:
    files_to_compress = []
    for root, dir_names, file_names in os.walk(folder_path):
      if exclusion_patterns:
        for dir_name in dir_names[:]:
          if any(fnmatch(dir_name, pattern.rstrip('/')) for pattern in exclusion_patterns):
            dir_names.remove(dir_name)

      for file_name in file_names:
        if exclusion_patterns and any(fnmatch(file_name, pattern) for pattern in exclusion_patterns):
          continue
        files_to_compress.append(os.path.join(root, file_name))

    if files_to_compress:
      with zipfile.ZipFile(tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as compressed_file:
        for file_path in files_to_compress:
          compressed_file.write(file_path, os.path.relpath(file_path, folder_path))

      shutil.move(tmp_zip_path, final_zip_path)

      if remove_original:
        shutil.rmtree(folder_path)

  except Exception as ex:
    logger.error(f'An error occurred while processing "{folder_name}":\n{ex}')
  finally:
    if os.path.exists(tmp_zip_path):
      os.remove(tmp_zip_path)

def extract_child_archives(
  parent_folder_path: str,
  remove_archives = True,
):
  logger.log(f'Extracting archives in "{parent_folder_path}"...')

  archives = []
  for root, _, files in os.walk(parent_folder_path, topdown = False):
    for file_name in files:
      if any(file_name.upper().endswith(f'.{ext}') for ext in ZIP_TYPES):
        archives.append(os.path.join(root, file_name))

  if archives:
    with ThreadPoolExecutor() as executor:
      list(tqdm(
        executor.map(lambda archive_path: extract_archive(archive_path, remove_archives), archives),
        total = len(archives),
        desc = f'Processing "{parent_folder_path}"'
      ))

    logger.success(f'Finished extracting archives in "{parent_folder_path}".')
  else:
    logger.warn(f'No archives found in "{parent_folder_path}".')

def extract_archive(
  archive_path: str,
  remove_archive = True,
):
  folder_name = os.path.splitext(os.path.basename(archive_path))[0]
  target_dir = os.path.join(os.path.dirname(archive_path), folder_name)

  if os.path.exists(target_dir):
    logger.trace(f'Skipping "{archive_path}". Folder exists.')
    return

  try:
    with zipfile.ZipFile(archive_path, 'r') as compressed_file:
      compressed_file.extractall(target_dir)

    if remove_archive:
      os.remove(archive_path)

  except Exception as ex:
    logger.error(f'An error occurred while processing "{folder_name}":\n{ex}')

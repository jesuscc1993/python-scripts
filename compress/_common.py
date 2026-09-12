import os
import shutil
import zipfile

from concurrent.futures import ThreadPoolExecutor
from fnmatch import fnmatch
from mtlogger import logger
from mtprompt import Prompt
from threading import Lock
from tqdm import tqdm

from _constants import FAILED, INCOMPLETE, SUCCEEDED, ZIP_TYPES

prompt_lock = Lock()

def compress_child_folders(
  parent_folder_path: str,
  output_type: str,
  remove_original = False,
  exclusion_patterns: list = None,
  min_depth = 1,
  max_depth = 1,
):
  logger.log(f'Compressing folders in "{parent_folder_path}"...')

  if max_depth < 1:
    logger.error('Depth must be 1 or greater.')
    return FAILED

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
      results = list(tqdm(
        executor.map(lambda folder: compress_folder(folder, output_type, remove_original, exclusion_patterns), folders),
        total = len(folders),
        desc = f'Processing "{parent_folder_path}"'
      ))

    status = get_status_from_results(results)

    if status == FAILED:
      logger.error(f'Failed to compress one or more folders in "{parent_folder_path}".')

    elif status == INCOMPLETE:
      logger.warn(f'One or more folders were not compressed in "{parent_folder_path}".')

    return status
  else:
    logger.warn(f'No folders found in "{parent_folder_path}".')
    return INCOMPLETE

def compress_folder(
  folder_path: str,
  output_type: str = ZIP_TYPES[0],
  remove_original = False,
  exclusion_patterns: list = None,
):
  folder_name = os.path.basename(folder_path)
  parent_dir = os.path.dirname(folder_path)

  zip_filename = f'{folder_name}.{output_type.lower()}'
  tmp_zip_path = os.path.join(parent_dir, f'.{zip_filename}.tmp')
  final_zip_path = os.path.join(parent_dir, zip_filename)
  already_exists = os.path.exists(final_zip_path)

  try:
    if already_exists:
      with prompt_lock:
        overwrite = Prompt.bool(f'\nArchive "{final_zip_path}" already exists. Overwrite?', default=False)

      if not overwrite:
        logger.warn(f'Skipping "{folder_path}". A compressed file with the same name already exists.')
        return INCOMPLETE

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
        for file_path in tqdm(files_to_compress, unit='file'):
          compressed_file.write(file_path, os.path.relpath(file_path, folder_path))

      os.replace(tmp_zip_path, final_zip_path)

      if remove_original:
        shutil.rmtree(folder_path)

      return SUCCEEDED

    logger.warn(f'No files found in "{folder_path}".')
    return INCOMPLETE

  except Exception as ex:
    logger.error(f'An error occurred while processing "{folder_name}":\n{ex}')
    return FAILED

  finally:
    try:
      if os.path.exists(tmp_zip_path):
        os.remove(tmp_zip_path)

    except Exception as cleanup_ex:
      logger.error(f'Unable to remove temporary archive "{tmp_zip_path}":\n{cleanup_ex}')
      return FAILED

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
      results = list(tqdm(
        executor.map(lambda archive_path: extract_archive(archive_path, remove_archives), archives),
        total = len(archives),
        desc = f'Processing "{parent_folder_path}"'
      ))

    status = get_status_from_results(results)

    if status == FAILED:
      logger.error(f'Failed to extract one or more archives in "{parent_folder_path}".')

    elif status == INCOMPLETE:
      logger.warn(f'One or more archives were not extracted in "{parent_folder_path}".')

    return status
  else:
    logger.warn(f'No archives found in "{parent_folder_path}".')
    return INCOMPLETE

def extract_archive(
  archive_path: str,
  remove_archive = True,
):
  folder_name = os.path.splitext(os.path.basename(archive_path))[0]
  target_dir = os.path.join(os.path.dirname(archive_path), folder_name)
  already_exists = os.path.exists(target_dir)

  try:
    if already_exists:
      with prompt_lock:
        overwrite = Prompt.bool(f'\nFolder "{target_dir}" already exists. Overwrite?', default=False)

      if not overwrite:
        logger.trace(f'Skipping "{archive_path}". Folder already exists.')
        return INCOMPLETE

    with zipfile.ZipFile(archive_path, 'r') as compressed_file:
      target_dir_abs = os.path.abspath(target_dir)
      for member in compressed_file.infolist():
        member_path = os.path.abspath(os.path.join(target_dir_abs, member.filename))

        if os.path.commonpath((target_dir_abs, member_path)) != target_dir_abs:
          raise ValueError(f'Archive member escapes target directory: "{member.filename}"')

      compressed_file.extractall(target_dir)

    if remove_archive and (not already_exists or overwrite):
      os.remove(archive_path)

    return SUCCEEDED

  except Exception as ex:
    logger.error(f'An error occurred while processing "{folder_name}":\n{ex}')
    return FAILED

def get_status_from_results(results):
  status = SUCCEEDED
  for result in results:
    if result == FAILED:
      return FAILED

    if result == INCOMPLETE:
      status = INCOMPLETE

  return status

import os
import shutil
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm

from _common import delete_empty_folders, get_volume_and_chapter, select_parent_folder, zfill_float

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the volume folders you want to merge:\n', process_parent_folder)

def process_parent_folder(
  parent_folder_path: str,
):
  files_to_process = []

  for folder in os.listdir(parent_folder_path):
    folder_path = os.path.join(parent_folder_path, folder)
    if os.path.isdir(folder_path):
      volume, chapter = get_volume_and_chapter(folder)
      if volume is None or chapter is None:
        tqdm.write(logger.format_warn(f'Skipping "{folder}". Volume or chapter numbers could not be inferred.'))
        continue

      output_path = os.path.join(parent_folder_path, f'Vol.{zfill_float(volume, 2)}')
      if not os.path.exists(output_path):
        os.makedirs(output_path)

      for item in os.listdir(folder_path):
        src = os.path.join(folder_path, item)
        if os.path.isfile(src):
          files_to_process.append((src, output_path, get_sanitized_chapter(chapter)))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{parent_folder_path}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

  delete_empty_folders(parent_folder_path)

  logger.success(f'Finished merging volumes in "{parent_folder_path}".')

def get_sanitized_chapter(
  chapter: str,
):
  parts = zfill_float(chapter, 3).split('.')
  name = parts[0]
  if len(parts) > 1: name += chr(ord('a') + int(parts[1]) - 1)
  return name

def process_file(
  params: tuple,
):
  src, target_folder, chapter = params
  base, ext = os.path.splitext(os.path.basename(src))
  new_name = f'ch{chapter}_p{base}{ext}'
  dest = os.path.join(target_folder, new_name)

  counter = 1
  while os.path.exists(dest):
    dest = os.path.join(target_folder, f'ch{chapter}_p{base}_{counter:02d}{ext}')
    counter += 1
  shutil.move(src, dest)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

import os
import shutil
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import LogLevel, logger
from mtprompt import Prompt
from tqdm import tqdm

from _common import delete_empty_folders, get_volume_and_chapter, select_parent_folder

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the volume folders you want to merge:\n', process_parent_folder)

def process_parent_folder(parent_dir):
  files_to_process = []

  for folder in os.listdir(parent_dir):
    folder_path = os.path.join(parent_dir, folder)
    if os.path.isdir(folder_path):
      volume, chapter = get_volume_and_chapter(folder)
      if not volume or not chapter:
        tqdm.write(logger.formatLevel(LogLevel.WARN, f'Skipping "{folder}". Volume or chapter numbers could not be inferred.'))
        continue

      output_path = os.path.join(parent_dir, f'Vol.{volume.zfill(2)}')
      if not os.path.exists(output_path):
        os.makedirs(output_path)

      for item in os.listdir(folder_path):
        src = os.path.join(folder_path, item)
        if os.path.isfile(src):
          files_to_process.append((src, output_path, get_sanitized_chapter(chapter)))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{parent_dir}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

  delete_empty_folders(parent_dir)

  logger.success(f'Finished merging volumes in "{parent_dir}".')

def get_sanitized_chapter(chapter):
  parts = chapter.split('.')
  name = f'{int(parts[0]):03d}'
  if len(parts) > 1: name += chr(ord('a') + int(parts[1]) - 1)
  return name

def process_file(params):
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
    logger.unhandledError(ex)
    Prompt.enter_to_exit()

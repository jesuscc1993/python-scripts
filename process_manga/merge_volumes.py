import os
import shutil
import re

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _common import select_parent_folder

def process_parent_folder(root_dir):
  files_to_process = []

  for folder in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder)
    if os.path.isdir(folder_path):
      volume, chapter = get_volume_and_chapter(folder)
      if not volume or not chapter:
        continue

      target_folder = os.path.join(root_dir, f'Vol.{volume.zfill(2)}')
      if not os.path.exists(target_folder):
        os.makedirs(target_folder)

      for item in os.listdir(folder_path):
        src = os.path.join(folder_path, item)
        if os.path.isfile(src):
          files_to_process.append((src, target_folder, chapter))

  with ThreadPoolExecutor() as executor, tqdm(total=len(files_to_process), desc=f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

  delete_empty_folders(root_dir)

def get_volume_and_chapter(folder_name):
  match = re.search(r'(Vol(?:ume)?)\.?\s*(\d+).*?(Ch(?:apter)?|Ep(?:isode)?)\.?\s*(\d+)', folder_name, re.IGNORECASE)
  return (match.group(2), match.group(4)) if match else (None, None)

def process_file(args):
  src, target_folder, chapter = args
  base, ext = os.path.splitext(os.path.basename(src))
  new_name = f'ch{chapter}_p{base}{ext}'
  dest = os.path.join(target_folder, new_name)

  counter = 1
  while os.path.exists(dest):
    dest = os.path.join(target_folder, f'ch{chapter}_p{base}_{counter:02d}{ext}')
    counter += 1
  shutil.move(src, dest)

def delete_empty_folders(parent_folder):
  for root, dirs, _ in os.walk(parent_folder, topdown=False):
    for dir_name in dirs:
      dir_path = os.path.join(root, dir_name)
      try:
        os.rmdir(dir_path)
      except OSError:
        pass

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder containing the chapter folders:\n', process_parent_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

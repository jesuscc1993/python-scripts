import os
import shutil
import re

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _common import delete_empty_folders, select_parent_folder

def process_parent_folder(root_dir):
  output_path = os.path.join(root_dir, 'output')
  if not os.path.exists(output_path):
    os.makedirs(output_path)

  files_to_process = []

  for folder in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder)
    if os.path.isdir(folder_path) and folder != 'output':
      chapter = get_chapter(folder)
      if not chapter:
        continue

      for item in os.listdir(folder_path):
        src = os.path.join(folder_path, item)
        if os.path.isfile(src):
          files_to_process.append((src, output_path, get_sanitized_chapter(chapter)))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

  delete_empty_folders(root_dir)

def get_chapter(folder_name):
  match = re.search(r'(Ch(?:apter)?|Ep(?:isode)?)\.?\s*(\d+(?:\.\d+)?)', folder_name, re.IGNORECASE)
  return match.group(2) if match else None

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
    select_parent_folder('Enter the path to the parent folder containing the chapter folders:\n', process_parent_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

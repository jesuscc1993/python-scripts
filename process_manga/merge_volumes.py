import os
import re
import shutil
import sys

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _common import delete_empty_folders, exit_with_prompt, print_error, select_parent_folder

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the volume folders you want to merge:\n', process_parent_folder)

def process_parent_folder(root_dir):
  files_to_process = []

  for folder in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder)
    if os.path.isdir(folder_path):
      volume, chapter = get_volume_and_chapter(folder)
      if not volume or not chapter:
        continue

      output_path = os.path.join(root_dir, f'Vol.{volume.zfill(2)}')
      if not os.path.exists(output_path):
        os.makedirs(output_path)

      for item in os.listdir(folder_path):
        src = os.path.join(folder_path, item)
        if os.path.isfile(src):
          files_to_process.append((src, output_path, get_sanitized_chapter(chapter)))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

  delete_empty_folders(root_dir)

def get_volume_and_chapter(folder_name):
  match = re.search(r'(Vol(?:ume)?)\.?\s*(\d+(?:\.\d+)?).*?(Ch(?:apter)?|Ep(?:isode)?)\.?\s*(\d+(?:\.\d+)?)', folder_name, re.IGNORECASE)
  return (match.group(2), match.group(4)) if match else (None, None)

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
    print_error(ex)
    exit_with_prompt()

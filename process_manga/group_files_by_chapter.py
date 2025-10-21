import os
import re
import shutil
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import LogLevel, logger
from tqdm import tqdm

from _common import delete_empty_folders, exit_with_prompt, print_error, select_parent_folder

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the folder containing the files you want to group by chapter:\n', process_parent_folder)

def process_parent_folder(root_dir):
  files_to_process = []

  for item in os.listdir(root_dir):
    item_path = os.path.join(root_dir, item)
    if os.path.isfile(item_path):
      chapter = get_chapter(item)
      if not chapter:
        tqdm.write(logger.format(LogLevel.WARN, f'Skipping "{item}". Chapter number could not be inferred.'))
        continue

      output_path = os.path.join(root_dir, f'Ch.{chapter.zfill(2)}')
      if not os.path.exists(output_path):
        os.makedirs(output_path)

      files_to_process.append((item_path, output_path, chapter))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

def get_chapter(filename):
  match = re.search(r'(Ch(?:apter)?|Ep(?:isode)?)\.?\s*(\d+(?:\.\d+)?)', filename, re.IGNORECASE)
  return match.group(2) if match else None

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

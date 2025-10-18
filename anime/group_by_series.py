import os
import shutil
import sys
import winsound

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the files you want to group:\n', process_parent_folder)

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

def play_notification_sound():
  winsound.MessageBeep(winsound.MB_ICONASTERISK)

def process_parent_folder(root_dir):
  files_to_process = []

  for item in os.listdir(root_dir):
    src = os.path.join(root_dir, item)
    if os.path.isfile(src):
      group_name = get_group_name(os.path.splitext(item)[0])
      output_path = os.path.join(root_dir, group_name)
      if not os.path.exists(output_path):
        os.makedirs(output_path)
      files_to_process.append((src, output_path))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

def get_group_name(filename):
  parts = filename.rsplit('-', 1)
  return parts[0].strip() if len(parts) > 1 else filename

def process_file(params):
  src, target_folder = params
  base, ext = os.path.splitext(os.path.basename(src))
  dest = os.path.join(target_folder, f'{base}{ext}')

  counter = 1
  while os.path.exists(dest):
    dest = os.path.join(target_folder, f'{base}_{counter:02d}{ext}')
    counter += 1
  shutil.move(src, dest)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('\nPress Enter to exit...')

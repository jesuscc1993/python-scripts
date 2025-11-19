import os
import re
import shutil
import sys
import winsound

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

PROTOCOL_MAP = {
  'com.epicgames.launcher': 'Epic Games'
}

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
    if os.path.isfile(src) and src.lower().endswith('.url'):
      client_name = get_client_name(src)
      if client_name:
        output_path = os.path.join(root_dir, client_name)
        if not os.path.exists(output_path):
          os.makedirs(output_path)
        files_to_process.append((src, output_path))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

def get_client_name(url_file):
  try:
    with open(url_file, 'r', encoding='utf-8') as f:
      for line in f:
        if line.strip().startswith('URL='):
          match = re.match(r'URL=(.+?)://', line)
          if match:
            protocol = match.group(1)
            if protocol in PROTOCOL_MAP:
              return PROTOCOL_MAP[protocol]
            parts = re.split(r'[-_]', protocol)
            return ' '.join(p.capitalize() for p in parts)
  except Exception as e:
    logger.error(f'Failed to read {url_file}: {e}')
  return None

def process_file(params):
  src, target_folder = params
  dest = os.path.join(target_folder, os.path.basename(src))
  shutil.move(src, dest)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('\nPress Enter to exit...')

import os
import re

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

from _sound_utils import play_notification_sound

def main():
  parent_folder = input('Enter the path to the parent folder containing the files:\n').strip(' "\'')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    logger.error(f'The specified path "{parent_folder}" is not a directory.')
  else:
    pattern = re.compile(input('Enter the pattern files need to match (regex):\n').strip(' "\''))
    process_files(parent_folder, pattern)
    play_notification_sound()
    logger.log(f'Finished processing "{parent_folder}".\n')
  main()

def process_files(parent_folder, pattern):
  files_to_process = []

  for root, _, files in os.walk(parent_folder):
    for file in files:
      if pattern.search(file):
        file_path = os.path.join(root, file)
        files_to_process.append(file_path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{parent_folder}"') as progress:
    for _ in executor.map(replace_file, files_to_process):
      progress.update(1)

def replace_file(file_path):
  with open(file_path, 'w') as file:
    file.write('')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

import os
import re
import winsound

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm

def main():
  parent_folder = Prompt.dir(
    'Enter the path to the parent folder containing the files'
  )
  pattern = re.compile(Prompt.str(
    'Enter the pattern files need to match (regex)'
  ))

  process_files(parent_folder, pattern)

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

  logger.success(f'Finished replacing files in "{parent_folder}".\n')

def replace_file(file_path):
  with open(file_path, 'w') as file:
    file.write('')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  winsound.MessageBeep()
  Prompt.enter_to_exit()

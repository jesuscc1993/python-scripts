import os
import stat
import subprocess
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt

META_FILES = ['.noxml', '.nomedia']

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    prompt_parent_folder()

def prompt_parent_folder():
  parent_folder = Prompt.dir(
    'Enter the path to the directory containing the folders you want to generate the metadata files for'
  )

  process_parent_folder(parent_folder)

def process_parent_folder(parent_folder):
  folders_to_process = [parent_folder]

  with os.scandir(parent_folder) as entries:
    for entry in entries:
      if entry.is_dir():
        folders_to_process.append(entry.path)

  with ThreadPoolExecutor(max_workers=1) as executor:
    executor.map(process_folder, folders_to_process)

def process_folder(folder_path):
  for filename in META_FILES:
    try:
      file_path = os.path.join(folder_path, filename)
      rel_path = os.path.relpath(file_path, os.path.dirname(folder_path))

      if os.path.exists(file_path):
        is_hidden = os.stat(file_path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN
        if is_hidden:
          logger.trace(f'Skipping "{rel_path}". File already exists.')
        else:
          subprocess.run(['attrib', '+h', file_path], check=False)
          logger.success(f'Hid existing "{rel_path}" file.')
      else:
        open(file_path, 'w').close()
        subprocess.run(['attrib', '+h', file_path], check=False)
        logger.success(f'Created hidden "{rel_path}" file.')

    except Exception as ex:
      logger.error(f'Could not create "{filename}":\n{ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

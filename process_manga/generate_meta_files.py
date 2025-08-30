import os
import sys

from concurrent.futures import ThreadPoolExecutor

from _common import exit_with_prompt, print_error
from _sound_utils import play_notification_sound

META_FILES = ['.noxml', '.nomedia']

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    prompt_parent_folder()

def prompt_parent_folder():
  parent_folder = input('Enter the path to the image you want to generate the metadata files for:\n')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'[ERROR] The specified path "{parent_folder}" is not a directory.')
  else:
    process_parent_folder(parent_folder)
    play_notification_sound()
    exit_with_prompt()

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
      if os.path.exists(file_path):
        print(f'[DEBUG] Skipping "{file_path}". File already exists.')
      else:
        open(file_path, 'w').close()
        os.system(f'attrib +h "{file_path}"')
        print(f'[LOG] Successfully created hidden file "{file_path}".')

    except Exception as ex:
      print(f'[ERROR] Could not create "{filename}": {ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()
import os

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _image_utils import is_image_file
from _sound_utils import play_notification_sound

def select_parent_folder(prompt, callback):
  parent_folder = input(prompt).strip(' "\'')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    callback(parent_folder)
    play_notification_sound()
    print(f'Finished processing "{parent_folder}".\n')
  select_parent_folder(prompt, callback)

def process_folder_images(folder_path, callback):
  files_to_process = []

  for root, _, files in os.walk(folder_path):
    for file in files:
      if is_image_file(file):
        file_path = os.path.join(root, file)
        files_to_process.append(file_path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{folder_path}"') as progress:
    for _ in executor.map(callback, files_to_process):
      progress.update(1)

def delete_empty_folders(folder_path):
  for root, dirs, _ in os.walk(folder_path, topdown = False):
    for dir_name in dirs:
      dir_path = os.path.join(root, dir_name)
      try:
        os.rmdir(dir_path)
      except OSError:
        pass

def print_error(error):
  print(f'An unexpected error occurred: {error}')

def exit_with_prompt():
  input('Press Enter to exit...')

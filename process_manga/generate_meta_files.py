import os
import sys

from concurrent.futures import ThreadPoolExecutor

META_FILES = ['.noxml', '.nomedia']

def prompt_parent_folder(default_folder=None):
  parent_folder = default_folder or input('Enter the path to the image you want to generate the palette for:\n')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    process_parent_folder(parent_folder)

def process_parent_folder(parent_folder):
  folders_to_process = []

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
        print(f'File "{file_path}" already exists. Skipping...')
      else:
        open(file_path, 'w').close()
        os.system(f'attrib +h "{file_path}"')
        print(f'Successfully created hidden file "{file_path}".')

    except Exception as e:
      print(f'ERROR: Failed to create "{filename}": {e}')

if __name__ == '__main__':
  try:
    parent_folder = sys.argv[1] if len(sys.argv) > 1 else None
    prompt_parent_folder(parent_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('Press Enter to exit...')
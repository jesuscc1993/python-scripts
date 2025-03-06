import os
import shutil
import zipfile

from tqdm import tqdm

from _sound_utils import play_notification_sound

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders you want to convert to CBR:\n')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    process_parent_folder(parent_folder)
    play_notification_sound()
    print(f'Finished processing "{parent_folder}".\n')
  main()

def process_parent_folder(parent_folder):
  for root, dirs, _ in os.walk(parent_folder):
    for dir_name in dirs:
      item_path = os.path.join(root, dir_name)
      process_folder(item_path)

  play_notification_sound()
  print(f'\nFinished compressing folders.')

def process_folder(folder_path):
  folder_name = os.path.basename(folder_path)
  cbz_file_path = f'{folder_path}.cbz'

  if os.path.exists(cbz_file_path):
    print(f'Skipping "{folder_name}". CBZ file with the same name already exists.')
    return

  try:
    with zipfile.ZipFile(cbz_file_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
      for root, _, files in os.walk(folder_path):
        for file in tqdm(files, desc=f'Processing "{folder_name}"'):
          file_path = os.path.join(root, file)
          cbz.write(file_path, os.path.relpath(file_path, folder_path))

    shutil.rmtree(folder_path)

  except Exception as e:
    print(f'An error occurred while processing "{folder_name}": {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

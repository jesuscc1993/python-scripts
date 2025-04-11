import os

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _image_utils import image_needs_resizing, is_image_file, is_image_uncompressed, resize_image, save_image_to_path
from _sound_utils import play_notification_sound

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders or images:\n').strip('" ')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    process_images(parent_folder)
    play_notification_sound()
    print(f'Finished processing "{parent_folder}".\n')
  main()

def process_images(root_dir):
  files_to_process = []

  for root, _, files in os.walk(root_dir):
    for file in files:
      if is_image_file(file):
        file_path = os.path.join(root, file)
        files_to_process.append(file_path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_image, files_to_process):
      progress.update(1)

def process_image(original_path):
  try:
    with Image.open(original_path) as img:
      needs_resizing = image_needs_resizing(img)
      needs_compression = is_image_uncompressed(original_path)

      if needs_resizing:
        img = resize_image(img)

      if needs_resizing or needs_compression:
        save_image_to_path(img, original_path)

  except Exception as e:
    print(f'Error processing "{original_path}": {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

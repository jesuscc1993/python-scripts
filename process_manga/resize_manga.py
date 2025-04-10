import os

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _image_utils import is_image_file, is_image_uncompressed, resize_image, save_image_to_path
from _sound_utils import play_notification_sound
from _settings import LONG_STRIP_ASPECT_RATIO, MAX_HEIGHT, MAX_WIDTH

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

def process_image(image_path):
  try:
    with Image.open(image_path) as img:
      width, height = img.size

      aspect_ratio = width / height
      is_long_strip = aspect_ratio <= LONG_STRIP_ASPECT_RATIO
      too_wide = is_long_strip and width > MAX_WIDTH
      too_tall = not is_long_strip and height > MAX_HEIGHT
      needs_resizing = too_wide or too_tall
      needs_compression = is_image_uncompressed(image_path)

      if needs_resizing:
        img = resize_image(img)

      if needs_resizing or needs_compression:
        output_path = save_image_to_path(img, image_path)
        if output_path != image_path:
          os.remove(image_path)

  except Exception as e:
    print(f'Error processing "{image_path}": {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

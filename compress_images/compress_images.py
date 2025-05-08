import os

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _image_utils import is_image_file
from _sound_utils import play_notification_sound

# settings
OUTPUT_FORMAT = 'WEBP'
OUTPUT_EXTENSION = OUTPUT_FORMAT.lower()
OUTPUT_QUALITY = 80

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders or images:\n').strip(' "\'')
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

def process_image(file_path):
  ext = os.path.splitext(file_path)[1].lower()
  name = os.path.splitext(file_path)[0]
  og_path = f'{name}.bak.{ext}'
  output_path = f'{name}.{OUTPUT_EXTENSION}'

  os.rename(file_path, og_path)

  with Image.open(og_path) as img:
    img.save(output_path, OUTPUT_FORMAT, quality = OUTPUT_QUALITY)

  if os.path.getsize(output_path) < os.path.getsize(og_path):
    os.remove(og_path)
  else:
    os.remove(output_path)
    os.rename(og_path, output_path)

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

import os
import sys

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

from _image_utils import is_image_file
from _settings import IMAGE_OUTPUT_FORMAT, IMAGE_OUTPUT_EXTENSION, IMAGE_OUTPUT_LOSSLESS_COMPRESSION, IMAGE_OUTPUT_QUALITY
from _common import select_parent_folder

def main():
  if len(sys.argv) > 1:
    compress_child_images(sys.argv[1])
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the images you want to compress:\n',
      compress_child_images
    )

def compress_child_images(root_dir):
  files_to_process = []

  for root, _, files in os.walk(root_dir):
    for file in files:
      if is_image_file(file):
        file_path = os.path.join(root, file)
        files_to_process.append(file_path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(compress_image, files_to_process):
      progress.update(1)

def compress_image(file_path):
  ext = os.path.splitext(file_path)[1].lower()
  name = os.path.splitext(file_path)[0]
  og_path = f'{name}.bak.{ext}'
  output_path = f'{name}.{IMAGE_OUTPUT_EXTENSION}'

  os.rename(file_path, og_path)

  with Image.open(og_path) as img:
    img.save(
      output_path,
      IMAGE_OUTPUT_FORMAT,
      lossless = IMAGE_OUTPUT_LOSSLESS_COMPRESSION,
      quality = 100 if IMAGE_OUTPUT_LOSSLESS_COMPRESSION else IMAGE_OUTPUT_QUALITY
    )

  if os.path.getsize(output_path) < os.path.getsize(og_path):
    os.remove(og_path)
  else:
    os.remove(output_path)
    os.rename(og_path, output_path)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

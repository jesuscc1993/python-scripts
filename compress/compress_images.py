import os
import sys

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

from _image_utils import WEBP_DIMENSION_LIMIT, is_image_file
from _settings import IMAGE_OUTPUT_FORMAT, IMAGE_OUTPUT_LOSSLESS_COMPRESSION, IMAGE_OUTPUT_QUALITY
from _common import select_parent_folder

output_ext = IMAGE_OUTPUT_FORMAT.lower()

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
      ext = os.path.splitext(file)[1].lower()
      if is_image_file(file) and ext != f'.{output_ext}':
        file_path = os.path.join(root, file)
        files_to_process.append(file_path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(compress_image, files_to_process):
      progress.update(1)

def compress_image(file_path):
  try:
    ext = os.path.splitext(file_path)[1].lower()
    name = os.path.splitext(file_path)[0]
    backup_path = f'{name}.bak{ext}'
    output_path = f'{name}.{output_ext}'

    os.rename(file_path, backup_path)

    with Image.open(backup_path) as img:
      if output_ext == 'webp':
        if img.width > WEBP_DIMENSION_LIMIT or img.height > WEBP_DIMENSION_LIMIT:
          logger.warn(f'Skipping "{file_path}" as the image\'s dimensions  ({img.width}px x {img.height}px) exceed WebP\'s limit of {WEBP_DIMENSION_LIMIT}px.')
          return

      img.save(
        output_path,
        IMAGE_OUTPUT_FORMAT,
        lossless = IMAGE_OUTPUT_LOSSLESS_COMPRESSION,
        quality = 100 if IMAGE_OUTPUT_LOSSLESS_COMPRESSION else IMAGE_OUTPUT_QUALITY
      )

    if os.path.exists(output_path) and os.path.getsize(output_path) < os.path.getsize(backup_path):
      os.remove(backup_path)
    else:
      os.remove(output_path)
      os.rename(backup_path, file_path)

  except Exception as ex:
    logger.error(f'Failed to compress "{file_path}": {ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

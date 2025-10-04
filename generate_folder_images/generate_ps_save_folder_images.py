import os

from PIL import Image
from mtlogger import logger

from _common import process_parent_folder, save_resized_image

IMAGE_FILENAME = 'ICON0.PNG'

def main():
  process_parent_folder(process_folder)

def process_folder(folder_path):
  image_path = os.path.join(folder_path, IMAGE_FILENAME)

  if not image_path:
    logger.warn(f' No suitable image found in "{folder_path}"')
    return

  with Image.open(image_path) as img:
    save_resized_image(img, folder_path)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')
import sys

from PIL import Image
from mtlogger import logger

from _common import exit_with_prompt, print_error, process_folder_images, select_parent_folder
from _image_utils import image_needs_resizing, is_image_uncompressed, resize_image, save_image_to_path

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the folders or images you want to resize:\n', process_parent_folder)

def process_parent_folder(folder_path):
  process_folder_images(folder_path, process_image)

def process_image(original_path):
  try:
    with Image.open(original_path) as img:
      needs_resizing = image_needs_resizing(img)
      needs_compression = is_image_uncompressed(original_path)

      if needs_resizing:
        img = resize_image(img)

      if needs_resizing or needs_compression:
        save_image_to_path(img, original_path)

  except Exception as ex:
    logger.log(f'Error processing "{original_path}": {ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()

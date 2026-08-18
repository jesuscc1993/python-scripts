import sys

from PIL import Image
from mtlogger import logger
from mtprompt import Prompt

from _common import process_folder_images, select_parent_folder
from _image_utils import image_needs_resizing, is_image_optimally_compressed, resize_image, save_image_to_path

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the folders or images you want to resize:\n', process_parent_folder)

def process_parent_folder(
  folder_path: str,
):
  process_folder_images(folder_path, process_image)

  logger.success(f'Finished resizing images in "{folder_path}".')

def process_image(
  img_path: str,
):
  try:
    with Image.open(img_path) as img:
      needs_resizing = image_needs_resizing(img)
      needs_compression = not is_image_optimally_compressed(img_path)

      if needs_resizing:
        img = resize_image(img)

      if needs_resizing or needs_compression:
        save_image_to_path(img, img_path)

  except Exception as ex:
    logger.error(f'Error processing "{img_path}":\n{ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
    Prompt.enter_to_exit()

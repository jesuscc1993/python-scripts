from PIL import Image

from _common import process_folder_images, select_parent_folder
from _image_utils import image_needs_resizing, is_image_uncompressed, resize_image, save_image_to_path

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

  except Exception as e:
    print(f'Error processing "{original_path}": {e}')

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder containing the folders or images:\n', process_parent_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

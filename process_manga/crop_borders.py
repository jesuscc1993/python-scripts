import numpy

from PIL import Image

from _common import process_folder_images, select_parent_folder
from _image_utils import resize_image, save_image_to_path
from _settings import WHITE_THRESHOLD

def process_parent_folder(folder_path):
  process_folder_images(folder_path, process_image)

def process_image(file_path):
  try:
    with Image.open(file_path) as img:
      img = crop_blanks(img)
      img = resize_image(img)
      save_image_to_path(img, file_path)
  except Exception as e:
    print(f'Failed to process {file_path}: {e}')

def crop_blanks(img):
  np_img = numpy.array(img)
  mask = numpy.any(np_img < WHITE_THRESHOLD, axis = 2)

  coords = numpy.argwhere(mask)
  if coords.size == 0:
    return img

  y0, x0 = coords.min(axis = 0)
  y1, x1 = coords.max(axis = 0) + 1

  cropped_array = np_img[y0:y1, x0:x1]
  cropped_img = Image.fromarray(cropped_array)
  return cropped_img

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder containing the folders or images:\n', process_parent_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

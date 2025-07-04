import numpy
import sys

from PIL import Image

from _common import exit_with_prompt, print_error, process_folder_images, select_parent_folder
from _image_utils import resize_image, save_image_to_path
from _settings import WHITE_THRESHOLD

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the folders or images you want to crop the borders of:\n', process_parent_folder)

def process_parent_folder(folder_path):
  process_folder_images(folder_path, process_image)

def process_image(file_path):
  try:
    with Image.open(file_path) as img:
      img = crop_blanks(img)
      img = resize_image(img)
      save_image_to_path(img, file_path)
  except Exception as ex:
    print(f'Failed to process {file_path}: {ex}')

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
    main()
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()

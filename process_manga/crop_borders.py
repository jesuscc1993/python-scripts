import numpy
import sys

from PIL import Image
from mtlogger import logger
from mtprompt import Prompt, to_dir

from _common import process_folder_images, select_parent_folder
from _image_utils import resize_image, save_image_to_path
from _settings import MAX_HEIGHT, MAX_WIDTH, WHITE_THRESHOLD

def main():
  if len(sys.argv) > 1:
    process_parent_folder(to_dir(sys.argv[1]))
  else:
    select_parent_folder('Enter the path to the parent folder containing the folders or images you want to crop the borders of:\n', process_parent_folder)

def process_parent_folder(
  folder_path: str,
):
  process_folder_images(folder_path, process_image)

  logger.success(f'Finished cropping borders in "{folder_path}".')

def process_image(
  file_path: str,
):
  try:
    with Image.open(file_path) as img:
      width, height = img.size
      if width > MAX_WIDTH or height > MAX_HEIGHT:
        cropped_img = crop_blanks(img)
        resized_img = resize_image(cropped_img)
        if resized_img.size != img.size:
          save_image_to_path(resized_img, file_path)
  except Exception as ex:
    logger.error(f'Could not process {file_path}:\n{ex}')

def crop_blanks(
  img: Image.Image,
):
  np_img = numpy.array(img)
  if np_img.ndim == 2:
    mask = np_img < WHITE_THRESHOLD
  else:
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
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

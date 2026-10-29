import numpy
import sys

from PIL import Image
from mtlogger import logger
from mtprompt import Prompt
from mtvalidation import to_dir

from _common import process_folder_images, select_parent_folder
from _image_utils import resize_image, save_image_to_path
from _settings import MAX_HEIGHT, MAX_WIDTH, WHITE_THRESHOLD


def main():
  if len(sys.argv) > 1:
    process_parent_folder(to_dir(sys.argv[1]))
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the folders or images you want to crop the borders of:\n',
      process_parent_folder,
    )


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
      should_crop_horizontally = width > MAX_WIDTH
      should_crop_vertically = height > MAX_HEIGHT
      if should_crop_horizontally or should_crop_vertically:
        cropped_img = crop_blanks(
          img,
          should_crop_horizontally,
          should_crop_vertically,
        )
        resized_img = resize_image(cropped_img)
        if resized_img.size != img.size:
          save_image_to_path(resized_img, file_path)
  except Exception as ex:
    logger.error(f'Could not process {file_path}:\n{ex}')


def crop_blanks(
  img: Image.Image,
  should_crop_horizontally: bool,
  should_crop_vertically: bool,
):
  np_img = numpy.array(img)
  if np_img.ndim == 2:
    mask = np_img < WHITE_THRESHOLD
  else:
    mask = numpy.any(np_img < WHITE_THRESHOLD, axis=2)

  image_height, image_width = mask.shape
  y0, y1 = 0, image_height
  x0, x1 = 0, image_width

  if should_crop_vertically:
    rows = numpy.any(mask, axis=1)
    if rows.any():
      y0 = numpy.argmax(rows)
      y1 = len(rows) - numpy.argmax(rows[::-1])

  if should_crop_horizontally:
    cols = numpy.any(mask, axis=0)
    if cols.any():
      x0 = numpy.argmax(cols)
      x1 = len(cols) - numpy.argmax(cols[::-1])

  if x0 == 0 and x1 == image_width and y0 == 0 and y1 == image_height:
    return img

  cropped_array = np_img[y0:y1, x0:x1]
  cropped_img = Image.fromarray(cropped_array)
  return cropped_img


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

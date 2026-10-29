import numpy
import os
import sys

from PIL import Image
from mtlogger import logger
from mtprompt import Prompt
from mtvalidation import to_dir

from _common import process_folder_images, select_parent_folder
from _image_utils import is_image_uncompressed, save_image_to_path
from _settings import BLACK_THRESHOLD, WHITE_THRESHOLD, MAX_PAGE_ASPECT_RATIO

# settings
HEIGHT_THRESHOLD = 48


def main():
  if len(sys.argv) > 1:
    process_parent_folder(to_dir(sys.argv[1]))
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the folders or images you want to crop the blanks of:\n',
      process_parent_folder,
    )


def process_parent_folder(
  folder_path: str,
):
  process_folder_images(folder_path, process_image)

  logger.success(f'Finished cropping webtoons in "{folder_path}".')


def process_image(
  file_path: str,
):
  try:
    with Image.open(file_path) as img:
      blank_free_image = crop_blanks(img)

      if image_needs_splitting(blank_free_image):
        save_image_splits(blank_free_image, file_path)
      elif blank_free_image.height != img.height or is_image_uncompressed(
        file_path
      ):
        save_image_to_path(blank_free_image, file_path)

  except Exception as ex:
    logger.error(f'Could not process {file_path}:\n{ex}')


def is_blank_strip(
  image_strip: numpy.ndarray,
):
  min_pixel = image_strip.min()
  max_pixel = image_strip.max()
  return min_pixel >= WHITE_THRESHOLD or max_pixel <= BLACK_THRESHOLD


def process_strip(
  strip: Image.Image,
  height: int,
):
  if height > HEIGHT_THRESHOLD:
    return strip.resize((strip.width, HEIGHT_THRESHOLD))
  return strip


def crop_blanks(
  img: Image.Image,
):
  width, height = img.size
  gray_pixels = numpy.asarray(img.convert('L'))
  blank_start = None
  content_start = 0
  has_blank_strip = False
  result_parts = []

  for y in range(0, height, HEIGHT_THRESHOLD):
    strip_end = min(y + HEIGHT_THRESHOLD, height)
    strip = gray_pixels[y:strip_end, :]

    if is_blank_strip(strip):
      has_blank_strip = True
      if blank_start is None:
        if content_start < y:
          result_parts.append(img.crop((0, content_start, width, y)))
        blank_start = y
    else:
      if blank_start is not None:
        blank_end = y
        blank_height = blank_end - blank_start
        blank_strip = img.crop((0, blank_start, width, blank_end))
        result_parts.append(process_strip(blank_strip, blank_height))
        blank_start = None
        content_start = y

  if blank_start is not None:
    blank_strip = img.crop((0, blank_start, width, height))
    result_parts.append(process_strip(blank_strip, height - blank_start))
  elif has_blank_strip:
    content_strip = img.crop((0, content_start, width, height))
    result_parts.append(content_strip)
  else:
    if img.mode != 'RGB':
      img = img.convert('RGB')
    if img.info:
      img.info.clear()
    return img

  final_height = sum(part.height for part in result_parts)
  stitched_image = Image.new('RGB', (width, final_height))
  current_y = 0
  for part in result_parts:
    stitched_image.paste(part, (0, current_y))
    current_y += part.height

  return stitched_image


def image_needs_splitting(
  img: Image.Image,
):
  width, height = img.size
  aspect_ratio = width / height
  return aspect_ratio < MAX_PAGE_ASPECT_RATIO


def save_image_splits(
  img: Image.Image,
  original_img_path: str,
):
  width, height = img.size
  split_height = int(width / MAX_PAGE_ASPECT_RATIO)
  num_splits = (height + split_height - 1) // split_height
  split_height = height // num_splits
  base_name, ext = os.path.splitext(original_img_path)

  try:
    for i in range(num_splits):
      top = i * split_height
      bottom = (i + 1) * split_height if i < num_splits - 1 else height
      split_image = img.crop((0, top, width, bottom))
      split_file_path = f'{base_name}.{i + 1}{ext}'
      save_image_to_path(split_image, split_file_path, keep=True)
    os.remove(original_img_path)

  except Exception as ex:
    logger.error(f'Could not save split images for {original_img_path}:\n{ex}')

    for i in range(num_splits):
      split_file_path = f'{base_name}.{i + 1}{ext}'
      if os.path.exists(split_file_path):
        os.remove(split_file_path)


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

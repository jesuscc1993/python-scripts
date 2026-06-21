import os

from PIL import Image
from mtlogger import logger

from _settings import LONG_STRIP_ASPECT_RATIO, MAX_HEIGHT, MAX_WIDTH, OUTPUT_FORMAT, OUTPUT_EXTENSION, OUTPUT_QUALITY

JPEG_EXTENSION = '.jpeg'
JPG_EXTENSION = '.jpg'
PNG_EXTENSION = '.png'
WEBP_EXTENSION = '.webp'

FILE_EXCLUSIONS = ['folder.jpg', 'cover.jpg']

def is_image_file(filename):
  name = filename.lower()
  return name.endswith((JPG_EXTENSION, JPEG_EXTENSION, PNG_EXTENSION, WEBP_EXTENSION)) and name not in FILE_EXCLUSIONS

def is_image_uncompressed(filename):
  return filename.lower().endswith(PNG_EXTENSION)

def is_image_optimally_compressed(filename):
  return filename.lower().endswith(WEBP_EXTENSION)

def get_max_dimensions(img):
  width, height = img.size

  aspect_ratio = width / height
  height_ratio = height / MAX_HEIGHT
  width_ratio = width / MAX_WIDTH
  is_portrait = height > width
  is_long_strip = aspect_ratio <= LONG_STRIP_ASPECT_RATIO
  too_wide = width > MAX_WIDTH and is_portrait
  too_tall = height > MAX_HEIGHT and not is_long_strip

  if too_wide and width_ratio > height_ratio:
    width = MAX_WIDTH
    height = int(width / aspect_ratio)
  elif too_tall:
    height = MAX_HEIGHT
    width = int(height * aspect_ratio)
  else:
    return None

  return (width, height)

def image_needs_resizing(img):
  return get_max_dimensions(img) is not None

def resize_image(img):
  new_dimensions = get_max_dimensions(img)
  if new_dimensions:
    return img.resize(new_dimensions, Image.LANCZOS)
  return img

def save_image_to_path(img, original_path, keep = False):
  try:
    output_path = f"{os.path.splitext(original_path)[0]}.{OUTPUT_EXTENSION}"
    img.save(output_path, OUTPUT_FORMAT, quality = OUTPUT_QUALITY)
    if not keep and output_path != original_path:
      os.remove(original_path)

  except Exception as ex:
    logger.error(f'Error processing "{original_path}":\n{ex}')

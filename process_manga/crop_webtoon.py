import os
import sys

from PIL import Image

from _common import process_folder_images, select_parent_folder
from _image_utils import save_image_to_path
from _settings import BLACK_THRESHOLD, WHITE_THRESHOLD, MAX_PAGE_ASPECT_RATIO

# settings
HEIGHT_THRESHOLD = 48

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the folders or images you want to crop the blanks of:\n', process_parent_folder)

def process_parent_folder(folder_path):
  process_folder_images(folder_path, process_image)

def process_image(file_path):
  try:
    with Image.open(file_path) as img:
      blank_free_image = crop_blanks(img)
      save_image_splits(blank_free_image, file_path)
  except Exception as e:
    print(f'Failed to process {file_path}: {e}')

def is_blank_strip(image_strip):
  gray_strip = image_strip.convert('L')
  min_pixel, max_pixel = gray_strip.getextrema()
  return min_pixel >= WHITE_THRESHOLD or max_pixel <= BLACK_THRESHOLD

def process_strip(strip, height):
  if height > HEIGHT_THRESHOLD:
    return strip.resize((strip.width, HEIGHT_THRESHOLD))
  return strip

def crop_blanks(img):
  width, height = img.size
  blank_start = None
  result_parts = []

  for y in range(0, height, HEIGHT_THRESHOLD):
    strip = img.crop((0, y, width, min(y + HEIGHT_THRESHOLD, height)))

    if is_blank_strip(strip):
      if blank_start is None:
        blank_start = y
    else:
      if blank_start is not None:
        blank_end = y
        blank_height = blank_end - blank_start
        blank_strip = img.crop((0, blank_start, width, blank_end))
        result_parts.append(process_strip(blank_strip, blank_height))
        blank_start = None
      result_parts.append(strip)

  if blank_start is not None:
    blank_strip = img.crop((0, blank_start, width, height))
    result_parts.append(process_strip(blank_strip, height - blank_start))

  final_height = sum(part.height for part in result_parts)
  stitched_image = Image.new('RGB', (width, final_height))
  current_y = 0
  for part in result_parts:
    stitched_image.paste(part, (0, current_y))
    current_y += part.height

  return stitched_image

def save_image_splits(img, original_path):
  width, height = img.size
  aspect_ratio = width / height
  if aspect_ratio < MAX_PAGE_ASPECT_RATIO:
    split_height = int(width / MAX_PAGE_ASPECT_RATIO)
    num_splits = (height + split_height - 1) // split_height
    split_height = height // num_splits
    base_name, ext = os.path.splitext(original_path)
    try:
      for i in range(num_splits):
        top = i * split_height
        bottom = (i + 1) * split_height if i < num_splits - 1 else height
        split_image = img.crop((0, top, width, bottom))
        split_file_path = f"{base_name}.{i + 1}{ext}"
        save_image_to_path(split_image, split_file_path, True)
      os.remove(original_path)
    except Exception as e:
      print(f'Failed to save split images for {original_path}: {e}')
      for i in range(num_splits):
        split_file_path = f"{base_name}.{i + 1}{ext}"
        if os.path.exists(split_file_path):
          os.remove(split_file_path)
  else:
    try:
      save_image_to_path(img, original_path)
    except Exception as e:
      print(f'Failed to save image {original_path}: {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

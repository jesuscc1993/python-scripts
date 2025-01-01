import os
import time
import winsound

from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# settings
HEIGHT_THRESHOLD = 48
WHITE_THRESHOLD = 248
BLACK_THRESHOLD = 8

JPG_EXTENSION = '.jpg'
JPEG_EXTENSION = '.jpeg'
PNG_EXTENSION = '.png'
WEB_EXTENSION = '.webp'

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders or images:\n')
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    start_time = time.time()
    process_images(parent_folder)
    elapsed_minutes = (time.time() - start_time) / 60
    winsound.MessageBeep(winsound.MB_ICONASTERISK)
    print(f'Finished processing "{parent_folder}" in {elapsed_minutes:.2f} minutes')

def process_images(parent_folder):
  tasks = []
  with ThreadPoolExecutor() as executor:
    for root, _, files in os.walk(parent_folder):
      for file in files:
        if is_image_file(file):
          file_path = os.path.join(root, file)
          tasks.append(executor.submit(process_image, file_path))

def process_image(file_path):
  try:
    with Image.open(file_path) as img:
      stitched_image = remove_and_stitch_blanks(img)
      stitched_image.save(file_path)
      print(f'Processed {file_path}')
  except Exception as e:
    print(f'Failed to process {file_path}: {e}')

def is_blank_strip(image_strip):
  gray_strip = image_strip.convert('L')
  extrema = gray_strip.getextrema()
  min_pixel, max_pixel = extrema
  return min_pixel >= WHITE_THRESHOLD or max_pixel <= BLACK_THRESHOLD

def process_strip(strip, height):
  if height > HEIGHT_THRESHOLD:
    return strip.resize((strip.width, HEIGHT_THRESHOLD))
  return strip

def remove_and_stitch_blanks(image):
  width, height = image.size
  blank_start = None
  result_parts = []

  for y in range(0, height, HEIGHT_THRESHOLD):
    strip = image.crop((0, y, width, min(y + HEIGHT_THRESHOLD, height)))

    if is_blank_strip(strip):
      if blank_start is None:
        blank_start = y
    else:
      if blank_start is not None:
        blank_end = y
        blank_height = blank_end - blank_start
        blank_strip = image.crop((0, blank_start, width, blank_end))
        result_parts.append(process_strip(blank_strip, blank_height))
        blank_start = None
      result_parts.append(strip)

  if blank_start is not None:
    blank_strip = image.crop((0, blank_start, width, height))
    result_parts.append(process_strip(blank_strip, height - blank_start))

  final_height = sum(part.height for part in result_parts)
  stitched_image = Image.new("RGB", (width, final_height))
  current_y = 0
  for part in result_parts:
    stitched_image.paste(part, (0, current_y))
    current_y += part.height

  return stitched_image

def is_image_file(filename):
  return filename.lower().endswith((JPG_EXTENSION, JPEG_EXTENSION, PNG_EXTENSION, WEB_EXTENSION))

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('Press Enter to exit...')

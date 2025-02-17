import os

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _image_utils import is_image_file
from _sound_utils import play_notification_sound

# settings
BLACK_THRESHOLD = 8
WHITE_THRESHOLD = 248
HEIGHT_THRESHOLD = 48

# MIN_PAGE_ASPECT_RATIO = 3/5
MAX_PAGE_ASPECT_RATIO = 1/5

OUTPUT_EXTENSION = '.webp'
OUTPUT_FORMAT = 'WEBP'
OUTPUT_QUALITY = 80

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders or images:\n')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    process_images(parent_folder)
    play_notification_sound()
    print(f'Finished processing "{parent_folder}".\n')
  main()

def process_images(root_dir):
  files_to_process = []

  for root, _, files in os.walk(root_dir):
    for file in files:
      if is_image_file(file):
        file_path = os.path.join(root, file)
        files_to_process.append(file_path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_image, files_to_process):
      progress.update(1)

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

def crop_blanks(image):
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
  stitched_image = Image.new('RGB', (width, final_height))
  current_y = 0
  for part in result_parts:
    stitched_image.paste(part, (0, current_y))
    current_y += part.height

  return stitched_image

def save_image_splits(image, original_path):
  width, height = image.size
  aspect_ratio = width / height
  if aspect_ratio < MAX_PAGE_ASPECT_RATIO:
    split_height = int(width / MAX_PAGE_ASPECT_RATIO)
    num_splits = (height + split_height - 1) // split_height
    split_height = height // num_splits
    base_name, ext = os.path.splitext(original_path)
    saved_files = []
    try:
      for i in range(num_splits):
        top = i * split_height
        bottom = (i + 1) * split_height if i < num_splits - 1 else height
        split_image = image.crop((0, top, width, bottom))
        split_file_path = f"{base_name}.{i + 1}{ext}"
        output_path = os.path.splitext(split_file_path)[0] + OUTPUT_EXTENSION
        split_image.save(output_path, OUTPUT_FORMAT, quality = OUTPUT_QUALITY)
        saved_files.append(split_file_path)
      os.remove(original_path)
    except Exception as e:
      print(f'Failed to save split images for {original_path}: {e}')
      for file_path in saved_files:
        if os.path.exists(file_path):
          os.remove(file_path)
  else:
    try:
      output_path = os.path.splitext(original_path)[0] + OUTPUT_EXTENSION
      image.save(output_path, OUTPUT_FORMAT, quality = OUTPUT_QUALITY)
      if output_path != original_path:
        os.remove(original_path)
    except Exception as e:
      print(f'Failed to save image {original_path}: {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

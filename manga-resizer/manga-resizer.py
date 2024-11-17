import os
import time
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# settings #
MAX_HEIGHT = 1200
OUTPUT_EXTENSION = '.jpg'
OUTPUT_FORMAT = 'JPEG'
OUTPUT_QUALITY = 100

JPG_EXTENSION = '.jpg'
JPEG_EXTENSION = '.jpeg'
PNG_EXTENSION = '.png'

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders or images:\n')
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    start_time = time.time()
    process_images(parent_folder)
    elapsed_minutes = (time.time() - start_time) / 60
    print(f'Finished processing "{parent_folder}" in {elapsed_minutes:.2f} minutes')

def process_images(root_dir):
  for root, _, files in os.walk(root_dir):
    print(f'Processing "{root}"')
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
      _ = [
        executor.submit(resize_image, os.path.join(root, file))
        for file in files if is_image_file(file)
      ]

def resize_image(image_path):
  try:
    # print(f'Processing "{image_path}"')
    with Image.open(image_path) as img:
      width, height = img.size
      needs_resizing = height > MAX_HEIGHT
      needs_compression = not is_image_jpeg(image_path)

      # discard alpha channel
      if img.mode != 'RGB':
        img = img.convert('RGB')

      # resize images larger than the target device
      if needs_resizing:
        new_height = MAX_HEIGHT
        new_width = int((new_height / height) * width)
        img = img.resize((new_width, new_height), Image.LANCZOS)

      # save when resized or uncompressed
      if needs_resizing or needs_compression:
        output_path = os.path.splitext(image_path)[0] + OUTPUT_EXTENSION
        img.save(output_path, OUTPUT_FORMAT, quality=OUTPUT_QUALITY)

        # delete the original file if they were replaced and save was successful
        if needs_compression:
          os.remove(image_path)

  except Exception as e:
    print(f'Error processing "{image_path}": {e}')

def is_image_file(filename):
  return filename.lower().endswith((JPG_EXTENSION, JPEG_EXTENSION, PNG_EXTENSION))

def is_image_jpeg(filename):
  return filename.lower().endswith((JPG_EXTENSION, JPEG_EXTENSION))

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('Press Enter to exit...')

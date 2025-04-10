import os
import numpy

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _image_utils import is_image_file, resize_image, save_image_to_path
from _settings import WHITE_THRESHOLD
from _sound_utils import play_notification_sound

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders or images:\n').strip('" ')
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
      save_image(blank_free_image, file_path)
  except Exception as e:
    print(f'Failed to process {file_path}: {e}')

def crop_blanks(img):
  np_img = numpy.array(img)
  mask = numpy.any(np_img < WHITE_THRESHOLD, axis=2)

  coords = numpy.argwhere(mask)
  if coords.size == 0:
    return img

  y0, x0 = coords.min(axis=0)
  y1, x1 = coords.max(axis=0) + 1

  cropped_array = np_img[y0:y1, x0:x1]
  cropped_img = Image.fromarray(cropped_array)
  return cropped_img

def save_image(img, file_path):
  try:
    img = resize_image(img)
    output_path = save_image_to_path(img, file_path)
    if output_path and output_path != file_path:
      os.remove(file_path)

  except Exception as e:
    print(f'Error processing "{img}": {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

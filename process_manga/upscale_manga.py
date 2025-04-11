import os
import subprocess

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _image_utils import is_image_file
from _settings import OUTPUT_EXTENSION
from _common import select_parent_folder

waifu2x_path = os.path.join(os.path.dirname(__file__), 'waifu2x/waifu2x.exe')

def process_parent_folder(root_dir):
  files_to_process = []

  for root, _, files in os.walk(root_dir):
    for file in files:
      if is_image_file(file):
        file_path = os.path.join(root, file)
        files_to_process.append(file_path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{root_dir}"') as progress:
    for _ in executor.map(process_image, files_to_process):
      progress.update(1)

def process_image(original_path):
  try:
    output_path = f'{original_path.rsplit(".", 1)[0]}@2x.{OUTPUT_EXTENSION}'

    subprocess.run([
      waifu2x_path,
      '-i', original_path,
      '-o', output_path,
      '-m', 'models-upconv_7_anime_style_art_rgb',
      '-n', '2',
      '-s', '2'
    ])

  except Exception as e:
    print(f'Error processing "{original_path}": {e}')

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder containing the folders or images:\n', process_parent_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

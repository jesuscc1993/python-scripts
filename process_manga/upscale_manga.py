import os
import subprocess

from _common import process_folder_images, select_parent_folder
from _settings import OUTPUT_EXTENSION

waifu2x_path = os.path.join(os.path.dirname(__file__), 'waifu2x/waifu2x.exe')

def process_parent_folder(folder_path):
  process_folder_images(folder_path, process_image)

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

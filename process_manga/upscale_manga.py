import os
import subprocess
import sys

from _common import select_parent_folder, process_folder_images

binary_path = os.path.join(os.path.dirname(__file__), 'binaries/realesrgan/realesrgan-ncnn-vulkan.exe')

def process_parent_folder(folder_path):
  process_folder_images(folder_path, process_image)

def process_image(file_path):
  try:
    subprocess.run(
      [
        binary_path,
        '-i', file_path,
        '-o', file_path,
        '-s', '2',
        '-n', 'realesr-animevideov3-x2'
      ],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL
    )

  except Exception as e:
    print(f'Error processing "{file_path}": {e}')

if __name__ == '__main__':
  try:
    if len(sys.argv) > 1:
      process_parent_folder(sys.argv[1])
    else:
      select_parent_folder('Enter the path to the parent folder containing the folders or images:\n', process_parent_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

import os
import subprocess
import sys

from mtlogger import logger

from _common import exit_with_prompt, print_error, process_folder_images, select_parent_folder

binary_path = os.path.join(os.path.dirname(__file__), 'binaries/realesrgan/realesrgan-ncnn-vulkan.exe')

def main():
  if len(sys.argv) > 1:
    process_parent_folder(sys.argv[1])
  else:
    select_parent_folder('Enter the path to the parent folder containing the folders or images you want to upscale:\n', process_parent_folder)

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

  except Exception as ex:
    logger.error(f'Could not process "{file_path}": {ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print_error(ex)
    exit_with_prompt()

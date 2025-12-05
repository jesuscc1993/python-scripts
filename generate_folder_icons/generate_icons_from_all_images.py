import os
import sys

from mtlogger import logger

from _common import image_to_ico, prompt_path

IMAGE_EXTS = [
  '.avif',
  '.bmp',
  '.gif',
  '.jpeg',
  '.jpg',
  '.png',
  '.tiff',
  '.webp',
]
ICON_SIZES = [16, 32, 48, 256]

def main():
  if len(sys.argv) > 1:
    parent_path = sys.argv[1]
  else:
    parent_path = prompt_path('Enter the folder path to process:\n')

  for root, _, files in os.walk(parent_path):
    for image_path in files:
      ext = os.path.splitext(image_path)[1].lower()
      if ext in IMAGE_EXTS:
        image_path = os.path.join(root, image_path)
        ico_path = os.path.join(root, os.path.splitext(image_path)[0] + '.ico')
        image_to_ico(image_path, ico_path, ICON_SIZES)
        logger.log(f'Generated "{ico_path}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

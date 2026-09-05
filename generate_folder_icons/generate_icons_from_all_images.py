import os
import sys

from mtlogger import logger
from mtprompt import Prompt, to_dir

from _common import image_to_ico

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
    parent_path = to_dir(sys.argv[1])
  else:
    parent_path = Prompt.dir(
      'Enter the path to the directory containing the images you want to process'
    )

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
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

import os
import sys
import winsound

from PIL import Image
from mtlogger import logger
from mtprompt import Prompt

from _constants import FOLDER_IMAGE_FILENAME, FOLDER_IMAGE_SIZE

def process_parent_folder(process_folder):
  if len(sys.argv) > 1:
    parent_folder = sys.argv[1]
  else:
    parent_folder = Prompt.dir('Enter the path to the parent folder containing the folders you want to generate icons for.\nLeave empty instead to provide and process a single folder instead.\nPARENT_FOLDER: ', optional=True)

    if not parent_folder:
      target_folder = Prompt.dir('\nEnter the path to the specific folder you want to generate an icon for:\nFOLDER: ')

      logger.log()
      process_folder(target_folder)

  logger.log('Generating cover images...')

  for root, dirs, _ in os.walk(parent_folder):
    for dir_name in dirs:
      item_path = os.path.join(root, dir_name)
      if os.path.exists(os.path.join(item_path, FOLDER_IMAGE_FILENAME)):
        logger.dim(f'  [{dir_name}] "{FOLDER_IMAGE_FILENAME}" already exists.')
        continue
      process_folder(item_path)

  winsound.MessageBeep()
  logger.log(f'Finished generating cover images.')

def resize_image(img, w, h):
  return img.resize((w, h), Image.LANCZOS)

def save_resized_image(img, folder_path):
  original_width, original_height = img.size

  if original_width > FOLDER_IMAGE_SIZE and original_height > FOLDER_IMAGE_SIZE:
    if original_width < original_height:
      new_width = FOLDER_IMAGE_SIZE
      new_height = int((FOLDER_IMAGE_SIZE / original_width) * original_height)
    else:
      new_height = FOLDER_IMAGE_SIZE
      new_width = int((FOLDER_IMAGE_SIZE / original_height) * original_width)

    img = resize_image(img, new_width, new_height)

  if img.mode == 'RGBA':
    background = Image.new('RGBA', img.size, (255, 255, 255, 0))
    background.paste(img, (0, 0), img)
    img = background

  output_file_path = os.path.join(folder_path, FOLDER_IMAGE_FILENAME)
  img.save(output_file_path)

  logger.debug(f'Saved {output_file_path}.\n')

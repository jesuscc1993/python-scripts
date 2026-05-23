import os
import winsound

from PIL import Image
from mtlogger import logger

from _constants import FOLDER_IMAGE_FILENAME, FOLDER_IMAGE_SIZE

def process_parent_folder(process_folder):
  parent_folder = input('Enter the path to the parent folder containing the folders you want to generate icons for.\nLeave empty instead to provide and process a single folder instead.\nPARENT_FOLDER: ').strip(' "\'')

  if parent_folder == '':
    target_folder = input('\nEnter the path to the specific folder you want to generate an icon for:\nFOLDER: ')

    if not os.path.isdir(target_folder):
      logger.error(f'The specified path "{target_folder}" is not a directory.')
      return

    logger.log()
    process_folder(target_folder)

  else:
    if not os.path.isdir(parent_folder):
      logger.error(f'The specified path "{parent_folder}" is not a directory.')
      return

    logger.log()

  for root, dirs, _ in os.walk(parent_folder):
    for dir_name in dirs:
      item_path = os.path.join(root, dir_name)
      if os.path.exists(os.path.join(item_path, FOLDER_IMAGE_FILENAME)):
        logger.debug(f'Skipping "{item_path}". "{FOLDER_IMAGE_FILENAME}" is already contained within.')
        continue
      process_folder(item_path)

  winsound.MessageBeep()
  logger.info(f'Finished generating icons.')

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

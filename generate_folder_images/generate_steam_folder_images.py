import os
import requests
import sys
import winsound

from PIL import Image
from io import BytesIO
from mtlogger import logger
from mtprompt import Prompt
from natsort import natsorted

from _common import resize_image
from _constants import JPEG_FORMAT, JPEG_QUALITY, FOLDER_IMAGE_FILENAME, FOLDER_IMAGE_H, FOLDER_IMAGE_W

ID_LENGTH = 7

CAPSULE_H = 353
CAPSULE_W = 616

RESIZE_HEIGHT = FOLDER_IMAGE_H
# RESIZE_WIDTH = math.ceil(CAPSULE_W * RESIZE_HEIGHT // CAPSULE_H)
RESIZE_WIDTH = 294

CROP_SIZE = FOLDER_IMAGE_W

COVER_URL_MAP = {
  'capsule': 'https://cdn.cloudflare.steamstatic.com/steam/apps/{}/capsule_616x353.jpg',
  'header': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/header.jpg',
  'library': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900.jpg'
}

def main():
  if len(sys.argv) > 1:
    parent_folder = sys.argv[1]
    cover_type = sys.argv[2] if len(sys.argv) > 2 else 'capsule'
    override_existing = sys.argv[3].lower() == 'y' if len(sys.argv) > 3 else False
  else:
    parent_folder, cover_type, override_existing = prompt_params()

  generate_covers(parent_folder, cover_type, override_existing)

def prompt_params():
  parent_folder = input('Enter the path to the parent folder containing your Steam saves:\n').strip(' "\'')
  logger.log()

  cover_type = input('Enter cover type (capsule, header, or library). Default is capsule:\n').strip().lower() or 'capsule'
  logger.log()

  override_existing = input('Override existing images? (y/N):\n').strip().lower() == 'y'
  logger.log()

  return parent_folder, cover_type, override_existing

def generate_covers(parent_folder, cover_type, override_existing):
  logger.log('Generating cover images...')

  cover_url = COVER_URL_MAP.get(cover_type)

  for folder_name in natsorted(os.listdir(parent_folder)):
    folder_path = os.path.join(parent_folder, folder_name)

    if os.path.isdir(folder_path) and folder_name.isdigit():
      process_folder(folder_path, folder_name, cover_url, override_existing)

  winsound.MessageBeep()
  logger.log('\nFinished generating cover images.')

def process_folder(folder_path, folder_name, cover_url, override_existing):
  cover_path = os.path.join(folder_path, FOLDER_IMAGE_FILENAME)
  formatted_name = folder_name.rjust(ID_LENGTH)

  if os.path.exists(cover_path) and not override_existing:
    logger.dim(f'  [{formatted_name}] {FOLDER_IMAGE_FILENAME} already exists.')
    return

  image_url = cover_url.format(folder_name)
  response = requests.get(image_url)

  if response.status_code == 200:
    img = Image.open(BytesIO(response.content))
    img = resize_image_to_fill(img, RESIZE_WIDTH, RESIZE_HEIGHT)
    img = crop_image(img, CROP_SIZE)
    img.save(cover_path, JPEG_FORMAT, quality = JPEG_QUALITY)

    logger.success(f'[{formatted_name}] Generated cover image.')
  else:
    logger.failure(f'[{formatted_name}] Could not download image (status code {response.status_code}).')

def resize_image_to_fill(img, w, h):
  new_scale = max(w / img.width, h / img.height)
  new_width = int(img.width * new_scale)
  new_height = int(img.height * new_scale)

  return resize_image(img, new_width, new_height)

def crop_image(img, crop_size):
  new_width = img.width
  new_height = img.height

  x0 = 0
  y0 = 0
  x1 = new_width
  y1 = new_height

  if new_width > crop_size:
    x0 = (new_width - crop_size) // 2
    x1 = x0 + crop_size

  if new_height > crop_size:
    y0 = (new_height - crop_size) // 2
    y1 = y0 + crop_size

  return img.crop((x0, y0, x1, y1))

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enterToExit()

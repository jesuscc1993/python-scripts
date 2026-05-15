import os
import requests
import sys
import winsound

from PIL import Image
from io import BytesIO
from mtlogger import logger
from natsort import natsorted

# settings
JPEG_FORMAT = 'JPEG'
JPEG_QUALITY = 100
TARGET_NAME = 'folder.jpg'
RESIZE_HEIGHT = 168
RESIZE_WIDTH = 294
CROP_SIZE = 256

COVER_URL_MAP = {
  'capsule': 'https://cdn.cloudflare.steamstatic.com/steam/apps/{}/capsule_616x353.jpg',
  'header': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/header.jpg',
  'library': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900.jpg'
}

def main():
  if len(sys.argv) > 1:
    cover_type = 'capsule'
    override_existing = False

    parent_folder = sys.argv[1]
    if len(sys.argv) > 2: cover_type = sys.argv[2]
    if len(sys.argv) > 3: override_existing = sys.argv[3].lower() == 'y'
  else:
    parent_folder, cover_type, override_existing = prompt_params()

  generate_covers(parent_folder, cover_type, override_existing)

def prompt_params():
  parent_folder = input('Enter the path to the parent folder containing your Steam saves:\n').strip(' "\'')
  logger.log()

  cover_type = input('Enter cover type (capsule, header, or library). Default is capsule:\n').strip().lower() or 'capsule'
  logger.log()

  override_existing = input('Override existing images? (y|n). Default: n:\n').strip().lower() == 'y'
  logger.log()

  return parent_folder, cover_type, override_existing

def generate_covers(parent_folder, cover_type, override_existing):
  cover_url = COVER_URL_MAP.get(cover_type)

  for folder_name in natsorted(os.listdir(parent_folder)):
    folder_path = os.path.join(parent_folder, folder_name)

    if os.path.isdir(folder_path) and folder_name.isdigit():
      process_folder(folder_path, folder_name, cover_url, override_existing)

  play_notification_sound()
  logger.log('\nFinished generating cover images.')

def process_folder(folder_path, folder_name, cover_url, override_existing):
  cover_path = os.path.join(folder_path, TARGET_NAME)
  formatted_name = folder_name.rjust(7)

  if os.path.exists(cover_path) and not override_existing:
    logger.debug(f'[{formatted_name}] SKIPPED: {TARGET_NAME} already exists.')
    return

  image_url = cover_url.format(folder_name)
  response = requests.get(image_url)

  if response.status_code == 200:
    img = Image.open(BytesIO(response.content))

    new_scale = max(RESIZE_WIDTH / img.width, RESIZE_HEIGHT / img.height)
    new_width = int(img.width * new_scale)
    new_height = int(img.height * new_scale)

    resized_img = img.resize((new_width, new_height), Image.LANCZOS)

    x0 = 0
    y0 = 0
    x1 = new_width
    y1 = new_height
    if new_width > CROP_SIZE:
      x0 = (new_width - CROP_SIZE) // 2
      x1 = x0 + CROP_SIZE
    if new_height > CROP_SIZE:
      y0 = (new_height - CROP_SIZE) // 2
      y1 = y0 + CROP_SIZE
    cropped_img = resized_img.crop((x0, y0, x1, y1))
    cropped_img.save(cover_path, JPEG_FORMAT, quality = JPEG_QUALITY)

    logger.log(f'[{formatted_name}] SUCCESS: Generated cover image for game ID.')
  else:
    logger.error(f'[{formatted_name}] FAILED:  Could not download image for game ID (status code {response.status_code}).')

def play_notification_sound():
  winsound.MessageBeep(winsound.MB_ICONASTERISK)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

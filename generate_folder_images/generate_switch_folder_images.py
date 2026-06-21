import os
import requests
import sys
import time
import json
import winsound

from PIL import Image
from io import BytesIO
from mtlogger import logger
from mtprompt import Prompt
from natsort import natsorted

from _common import resize_image
from _constants import JPEG_FORMAT, JPEG_QUALITY, FOLDER_IMAGE_FILENAME, FOLDER_IMAGE_W, REQ_TIMEOUT

ID_LENGTH = 16
SWITCH_MAPPING_URL = 'https://www.eliboa.com/switch/nsw_titles.php?export=json'
CACHE_FILENAME = 'nsw_titles.json'
CACHE_TTL = 24 * 60 * 60

def main():
  if len(sys.argv) > 1:
    parent_folder = sys.argv[1]
    override_existing = sys.argv[2].lower() == 'y' if len(sys.argv) > 2 else False
  else:
    parent_folder, override_existing = prompt_params()

  generate_covers(parent_folder, override_existing)

def prompt_params():
  parent_folder = Prompt.dir(
    'Enter the path to the parent folder containing your Switch saves'
  )
  override_existing = Prompt.bool(
    'Override existing images?',
    default=False
  )

  return parent_folder, override_existing

def generate_covers(parent_folder, override_existing):
  logger.log('Generating cover images...')

  mapping = load_switch_mapping()

  for folder_name in natsorted(os.listdir(parent_folder)):
    folder_path = os.path.join(parent_folder, folder_name)

    if os.path.isdir(folder_path):
      process_folder(folder_path, folder_name, mapping.get(folder_name), override_existing)

  winsound.MessageBeep()
  logger.log('\nFinished generating cover images.')

def process_folder(folder_path, folder_name, entry, override_existing):
  formatted_name = folder_name.rjust(ID_LENGTH)
  cover_path = os.path.join(folder_path, FOLDER_IMAGE_FILENAME)

  if os.path.exists(cover_path) and not override_existing:
    logger.trace(f'  [{formatted_name}] {FOLDER_IMAGE_FILENAME} already exists.')
    return

  image_url = entry.get('iconUrl') if entry else None
  if not image_url:
    logger.trace(f'  [{formatted_name}] no cover found.')
    return

  try:
    response = requests.get(image_url)
    response.raise_for_status()
  except Exception as ex:
    logger.failure(f'[{formatted_name}] Could not download {image_url}:\n{ex}')
    return

  img = Image.open(BytesIO(response.content))
  img = resize_image(img, FOLDER_IMAGE_W, FOLDER_IMAGE_W)
  img.save(cover_path, JPEG_FORMAT, quality = JPEG_QUALITY)

  logger.success(f'[{formatted_name}] Generated cover image.')

def read_cached_mapping(path):
  if not os.path.exists(path) or time.time() - os.path.getmtime(path) >= CACHE_TTL:
    return None

  with open(path, 'r', encoding='utf-8') as fh:
    return json.load(fh)

def load_switch_mapping():
  path = os.path.join(os.path.dirname(__file__), 'cache', CACHE_FILENAME)

  try:
    cached = read_cached_mapping(path)
    if cached is not None:
      return cached
  except Exception:
    pass

  try:
    resp = requests.get(SWITCH_MAPPING_URL, timeout=REQ_TIMEOUT)
    resp.raise_for_status()
    mapping = resp.json().get('game_titles', {})

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
      json.dump(mapping, fh)

    return mapping
  except Exception as ex:
    logger.error(f'Failed to load switch mapping:\n{ex}')

    try:
      if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as fh:
          return json.load(fh)
    except Exception:
      pass

    return {}

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

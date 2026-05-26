import os
import re
import requests
import sys
import winsound

from PIL import Image
from io import BytesIO
from mtlogger import logger
from mtprompt import Prompt
from natsort import natsorted

from _common import resize_image
from _constants import JPEG_FORMAT, JPEG_QUALITY, FOLDER_IMAGE_FILENAME, FOLDER_IMAGE_W, REQ_TIMEOUT

CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

TWITCH_AUTH_URL = 'https://id.twitch.tv/oauth2/token'
IGDB_API_URL = 'https://api.igdb.com/v4/games'

ACCESS_TOKEN = None

def main():
  if len(sys.argv) > 1:
    parent_folder = sys.argv[1]
    override_existing = sys.argv[2].lower() == 'y' if len(sys.argv) > 2 else False
  else:
    parent_folder, override_existing = prompt_params()

  generate_covers(parent_folder, override_existing)

def prompt_params():
  parent_folder = Prompt.dir(
    'Enter the path to the parent folder containing your games'
    )
  override_existing = Prompt.bool(
    'Override existing images?',
    default=False
  )

  return parent_folder, override_existing

def generate_covers(parent_folder, override_existing):
  if not os.path.isdir(parent_folder):
    logger.error(f'The specified path "{parent_folder}" is not a directory.')
    return

  logger.log('Generating cover images...')

  for folder_name in natsorted(os.listdir(parent_folder)):
    folder_path = os.path.join(parent_folder, folder_name)

    if os.path.isdir(folder_path):
      process_folder(folder_path, folder_name, override_existing)

  winsound.MessageBeep()
  logger.log('\nFinished generating cover images.')

def get_access_token():
  global ACCESS_TOKEN

  if ACCESS_TOKEN:
    return ACCESS_TOKEN

  if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError('TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET must be set.')

  try:
    response = requests.post(
      TWITCH_AUTH_URL,
      params={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
      },
      timeout=REQ_TIMEOUT
    )
    response.raise_for_status()
    ACCESS_TOKEN = response.json().get('access_token')
    return ACCESS_TOKEN
  except Exception as ex:
    logger.error(f'Could not get access token:\n{ex}')

  return None

def split_camel_case(name):
  return re.sub(r'([a-z])([A-Z])', r'\1 \2', name)

def get_cover_image(query):
  query = split_camel_case(query)
  access_token = get_access_token()
  body = f'fields name,cover.url; search "{query}"; limit 1;'

  try:
    response = requests.post(
      IGDB_API_URL,
      headers={
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
      },
      data=body,
      timeout=REQ_TIMEOUT
    )
    response.raise_for_status()

    games = response.json()
    cover_url = games[0].get('cover', {}).get('url') if games else None
    return f'https:{cover_url.replace("t_thumb", "t_cover_big")}' if cover_url else None

  except Exception as ex:
    logger.error(f'Could not fetch data for game {query}:\n{ex}')

  return None

def download_image(image_url):
  try:
    response = requests.get(image_url, timeout=REQ_TIMEOUT)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))
  except Exception as ex:
    logger.error(f'Could not download {image_url}:\n{ex}')

  return None

def save_image(img, save_path):
  try:
    if img.mode != 'RGB':
      img = img.convert('RGB')
    img = resize_image(img, FOLDER_IMAGE_W, FOLDER_IMAGE_W)
    img.save(save_path, JPEG_FORMAT, quality = JPEG_QUALITY)
  except Exception as ex:
    logger.error(f'Could not save "{save_path}":\n{ex}')

def process_folder(folder_path, folder_name, override_existing):
  cover_path = os.path.join(folder_path, FOLDER_IMAGE_FILENAME)

  if os.path.exists(cover_path) and not override_existing:
    logger.dim(f'  [{folder_name}] {FOLDER_IMAGE_FILENAME} already exists.')
    return

  try:
    image_url = get_cover_image(folder_name)
    if not image_url:
      logger.dim(f'  [{folder_name}] no cover found.')
      return

    img = download_image(image_url)
    if not img:
      logger.failure(f'[{folder_name}] Could not download {image_url}.')
      return

    save_image(img, cover_path)
    logger.success(f'[{folder_name}] Generated cover image.')
  except Exception as ex:
    logger.failure(f'[{folder_name}] Could not process folder:\n{ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enter_to_exit()

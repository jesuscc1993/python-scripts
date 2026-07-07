import os
import requests

from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from mtlogger import logger
from mtprompt import Prompt

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

COVER_H = os.environ.get('COVER_H')
COVER_W = os.environ.get('COVER_W')
HEADER_H = os.environ.get('HEADER_H')
HEADER_W = os.environ.get('HEADER_W')

COVER_H = int(COVER_H) if COVER_H else None
COVER_W = int(COVER_W) if COVER_W else None
HEADER_H = int(HEADER_H) if HEADER_H else None
HEADER_W = int(HEADER_W) if HEADER_W else None

# settings
TERMS_BLACKLIST = ['soundtrack', 'artbook']
OUTPUT_FOLDER = os.path.join('output', 'assets')

SEARCH_URL = 'https://store.steampowered.com/api/storesearch/'
SEARCH_PARAMS = {'term': '', 'l': 'english', 'cc': 'US'}
RESPONSE_NAME = 'name'

COVER_URL_MAP = {
  'header': {
    'url': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/header.jpg',
    'dest': '{}.jpg',
    'size': [HEADER_W, HEADER_H] if HEADER_W and HEADER_H else None
  },
  'library': {
    'url': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900.jpg',
    'dest': '{}p.jpg',
    'size': [COVER_W, COVER_H] if COVER_W and COVER_H else None
  }
}

session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0'}

def main():
  while True:
    name = Prompt.str('Enter the name of the game')
    items = search_game(name)
    if not items:
      logger.warn('No results found.')
      logger.hr()
      continue

    items = [
      item for item in items
      if all(word not in item.get(RESPONSE_NAME, '').lower() for word in TERMS_BLACKLIST)
    ]

    if len(items) == 1:
      choice = 1
      logger.log(f'\n1. {items[0].get(RESPONSE_NAME)} ({items[0].get("id")})')
    else:
      logger.log('Matches found:')
      for i, item in enumerate(items, 1):
        logger.log(f"{i}. {item.get(RESPONSE_NAME)} ({item.get('id')})")

      choice = Prompt.int('Select a match', default=1)
      if not (1 <= choice <= len(items)):
        logger.error('Invalid selection.')
        logger.hr()
        continue

      selected = items[choice - 1]
      download_game_assets(selected.get('id'))
      break

def search_game(name):
  params = SEARCH_PARAMS.copy()
  params['term'] = name

  try:
    response = session.get(SEARCH_URL, params = params, headers = headers)
    response.raise_for_status()
    return response.json().get('items', [])
  except Exception as ex:
    logger.error(f'Error searching for game "{name}":\n{ex}')
    return []

def download_game_assets(appid):
  output_dir = os.path.join(os.getcwd(), OUTPUT_FOLDER)
  os.makedirs(output_dir, exist_ok = True)

  for _, data in COVER_URL_MAP.items():
    url = data['url'].format(appid)
    filename = data['dest'].format(appid)
    size = data.get('size')
    filepath = os.path.join(output_dir, filename)

    try:
      response = session.get(url, headers = headers)
      response.raise_for_status()
    except Exception as ex:
      logger.error(f'Could not download {url}:\n{ex}')
      continue

    save_asset(response.content, filepath, size)

def save_asset(content, filepath, size = None):
  try:
    img = Image.open(BytesIO(content))
    if size: img = img.resize(size, Image.LANCZOS)
    img.save(filepath)
    logger.success(f'Saved "{filepath}"')
  except Exception as ex:
    logger.error(f'Could not save {filepath}:\n{ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

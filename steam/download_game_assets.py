import os
import requests

from PIL import Image
from io import BytesIO
from mtlogger import logger
from mtprompt import Prompt

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
    'size': [220, 103] # remove to keep original size
  },
  'library': {
    'url': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900.jpg',
    'dest': '{}p.jpg',
    'size': [160, 240] # remove to keep original size
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

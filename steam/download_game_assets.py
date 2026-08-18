import os
import requests

from mtlogger import logger
from mtprompt import Prompt

from _common import download_assets_for_app_id

# settings
TERMS_BLACKLIST = ['soundtrack', 'artbook']
OUTPUT_FOLDER = os.path.join('output', 'assets')

SEARCH_URL = 'https://store.steampowered.com/api/storesearch/'
SEARCH_PARAMS = {'term': '', 'l': 'english', 'cc': 'US'}
RESPONSE_NAME = 'name'

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
      download_assets_for_app_id(selected.get('id'), os.path.join(os.getcwd(), OUTPUT_FOLDER))
      break

def search_game(
  name: str,
):
  params = SEARCH_PARAMS.copy()
  params['term'] = name

  try:
    response = session.get(SEARCH_URL, params = params, headers = headers)
    response.raise_for_status()
    return response.json().get('items', [])
  except Exception as ex:
    logger.error(f'Error searching for game "{name}":\n{ex}')
    return []


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

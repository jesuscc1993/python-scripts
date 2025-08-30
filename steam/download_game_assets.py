import os
import requests

from PIL import Image
from io import BytesIO

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
    name = input('Enter the name of the game: ').strip()
    if not name: break

    items = search_game(name)
    if not items:
      print('[WARN] No results found.')
      continue

    items = [
      item for item in items
      if all(word not in item.get(RESPONSE_NAME, '').lower() for word in TERMS_BLACKLIST)
    ]

    if len(items) == 1:
      choice = 1
      print(f'\n1. {items[0].get(RESPONSE_NAME)} ({items[0].get("id")})')
    else:
      print('\nSelect a result (default = 1):')
      for i, item in enumerate(items, 1):
        print(f"{i}. {item.get(RESPONSE_NAME)} ({item.get('id')})")

      try:
        choice = int(input('').strip() or '1')
        if not (1 <= choice <= len(items)):
          print('[ERROR] Invalid selection.')
          continue
      except ValueError:
        print('[ERROR] Invalid input.')
        continue

    print('')
    selected = items[choice - 1]
    download_game_assets(selected.get('id'))
    print('')

def search_game(name):
  params = SEARCH_PARAMS.copy()
  params['term'] = name

  response = session.get(SEARCH_URL, params = params, headers = headers)
  return response.json().get('items', []) if response.ok else []

def download_game_assets(appid):
  output_dir = os.path.join(os.getcwd(), OUTPUT_FOLDER)
  os.makedirs(output_dir, exist_ok = True)

  for key, data in COVER_URL_MAP.items():
    url = data['url'].format(appid)
    filename = data['dest'].format(appid)
    size = data.get('size')
    filepath = os.path.join(output_dir, filename)

    response = session.get(url, headers = headers)
    if response.ok:
      save_asset(response.content, filepath, size)
    else:
      print(f'[ERROR] Could not download {key} image.')

def save_asset(content, filepath, size = None):
  try:
    img = Image.open(BytesIO(content))
    if size: img = img.resize(size, Image.LANCZOS)
    img.save(filepath)
    print(f'Saved: {filepath}')
  except Exception:
    print(f'[ERROR] Could not save asset at {filepath}')

main()

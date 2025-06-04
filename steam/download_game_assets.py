import os
import requests

OUTPUT_FOLDER = os.path.join('output', 'assets')

SEARCH_URL = 'https://store.steampowered.com/api/storesearch/'
SEARCH_PARAMS = {'term': '', 'l': 'english', 'cc': 'US'}

COVER_URL_MAP = {
  'header': {
    'src': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/header.jpg',
    'dest': '{}.jpg'
  },
  'library': {
    'src': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900.jpg',
    'dest': '{}p.jpg'
  }
}

session = requests.Session()
headers = {'User-Agent': 'Mozilla/5.0'}

def main():
  while True:
    name = input('Enter the name of the game: ').strip()
    if not name:
      break

    items = searchGame(name)
    if not items:
      print('No results found.')
      continue


    if len(items) == 1:
      choice = 1
      print(f'\n1. {items[0].get("name")} ({items[0].get("id")})')
    else:
      print('\nSelect a result (default = 1):')
      for i, item in enumerate(items, 1):
        print(f"{i}. {item.get('name')} ({item.get('id')})")

      try:
        choice = int(input('').strip() or '1')
        if not (1 <= choice <= len(items)):
          print('Invalid selection.')
          continue
      except ValueError:
        print('Invalid input.')
        continue

    print('')
    selected = items[choice - 1]
    downloadGameAssets(selected.get('id'))
    print('')

def searchGame(name):
  params = SEARCH_PARAMS.copy()
  params['term'] = name

  response = session.get(SEARCH_URL, params = params, headers = headers)

  if not response.ok:
    return []

  data = response.json()
  return data.get('items', [])

def downloadGameAssets(appid):
  output_dir = os.path.join(os.getcwd(), OUTPUT_FOLDER)
  os.makedirs(output_dir, exist_ok = True)

  for key, data in COVER_URL_MAP.items():
    url = data['src'].format(appid)
    filename = data['dest'].format(appid)
    filepath = os.path.join(output_dir, filename)

    response = session.get(url, headers = headers)
    if response.ok:
      with open(filepath, 'wb') as f:
        f.write(response.content)
      print(f'Downloaded: {filepath}')
    else:
      print(f'Failed to download {key} image.')

main()
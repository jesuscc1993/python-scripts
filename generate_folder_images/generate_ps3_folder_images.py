import os
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from _common import process_parent_folder, save_resized_image

BASE_URL = 'https://wiki.rpcs3.net'
SEARCH_URL = BASE_URL + "/index.php?search={game_id}"

def main():
  process_parent_folder(process_folder)

def process_folder(folder_path):
  match = re.match(r'([A-Za-z]+\d+)', os.path.basename(os.path.normpath(folder_path)))

  if match:
    game_id = match.group(1)
  else:
    print(f'[ERROR] Could not extract a valid game ID from "{folder_path}"')
    return

  download_game_cover(game_id, folder_path)

def download_game_cover(game_id, folder_path):
  search_url = SEARCH_URL.format(game_id = game_id)
  response = requests.get(search_url)

  if response.status_code != 200:
    print(f'[ERROR] Could not access the search results for {game_id}. Status code: {response.status_code}')
    return

  soup = BeautifulSoup(response.text, 'html.parser')
  game_link = soup.select_one('.mw-search-result-heading a')
  if not (game_link and 'href' in game_link.attrs):
    print(f'[WARN] No game found for ID {game_id}.')
    return

  game_page_url = f'{BASE_URL}{game_link["href"]}'
  game_response = requests.get(game_page_url)
  if game_response.status_code != 200:
    print(f'[ERROR] Could not access the game page. Status code: {game_response.status_code}')
    return

  game_soup = BeautifulSoup(game_response.text, 'html.parser')
  image_tag = game_soup.select_one('.citizen-body-container .image img')
  if not (image_tag and 'src' in image_tag.attrs):
    print(f'[WARN] Cover image not found for game ID {game_id}.')
    return

  image_url = f'{BASE_URL}{image_tag["src"]}'
  image_response = requests.get(image_url)
  if image_response.status_code != 200:
    print(f'[ERROR] Could not download image from {image_url}.')
    return

  img = Image.open(BytesIO(image_response.content))
  save_resized_image(img, folder_path)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'[ERROR] An unexpected error occurred: {ex}')
  input('Press Enter to exit...')
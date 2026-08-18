import os
import re
import requests

from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO
from mtlogger import logger
from mtprompt import Prompt

from _common import process_parent_folder, save_resized_image

SEARCH_URL = 'https://cdromance.org/?s={game_id}'

def main():
  process_parent_folder(process_folder)

def process_folder(
  folder_path: str,
):
  match = re.match(r'([A-Za-z]+\d+)', os.path.basename(os.path.normpath(folder_path)))

  if match:
    game_id = match.group(1)
    game_id = re.sub(r'([A-Za-z]+)(\d+)', r'\1-\2', game_id)
  else:
    logger.warn(f'Could not extract a valid game ID from "{folder_path}"')
    return

  download_game_cover(game_id, folder_path)

def download_game_cover(
  game_id: str,
  folder_path: str,
):
  try:
    search_url = SEARCH_URL.format(game_id = game_id)
    response = requests.get(search_url)
    response.raise_for_status()
  except Exception as ex:
    logger.error(f'Could not access the search results for {game_id}:\n{ex}')
    return

  soup = BeautifulSoup(response.text, 'html.parser')
  game_link = soup.select_one('.game-container a')
  if not (game_link and 'href' in game_link.attrs):
    logger.warn(f'No game found for ID {game_id}.')
    return

  try:
    game_page_url = game_link['href']
    game_response = requests.get(game_page_url)
    game_response.raise_for_status()
  except Exception as ex:
    logger.error(f'Could not fetch game data for ID {game_id}:\n{ex}')
    return

  game_soup = BeautifulSoup(game_response.text, 'html.parser')
  image_tag = game_soup.select_one('.wp-post-image')
  if not (image_tag and 'src' in image_tag.attrs):
    logger.warn(f'Cover image not found for game ID {game_id}.')
    return

  try:
    image_url = image_tag['src']
    image_response = requests.get(image_url)
    image_response.raise_for_status()
  except Exception as ex:
    logger.error(f'Could not download {image_url}:\n{ex}')
    return

  img = Image.open(BytesIO(image_response.content))
  save_resized_image(img, folder_path)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

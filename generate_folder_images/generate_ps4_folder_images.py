import os
import re
import requests

from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO
from mtlogger import logger
from mtprompt import Prompt

from _common import process_parent_folder, save_resized_image

TITLE_URL = 'https://serialstation.com/titles/{game_id}'

def main():
  process_parent_folder(process_folder)

def process_folder(folder_path):
  game_id = os.path.basename(os.path.normpath(folder_path))
  download_game_cover(game_id, folder_path)

def download_game_cover(game_id, folder_path):
  try:
    url = TITLE_URL.format(game_id=re.sub(r'([A-Za-z]+)(\d+)', r'\1/\2', game_id))
    response = requests.get(url)
    response.raise_for_status()
  except Exception as ex:
    logger.error(f'Could not fetch game data {url}:\n{ex}')
    return

  soup = BeautifulSoup(response.text, 'html.parser')
  image_tag = soup.select_one('.wp-post-image')
  if not (image_tag and 'src' in image_tag.attrs):
    logger.warn(f'No cover image found for game ID {game_id}.')
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
  logger.success(f'Saved image for game ID {game_id}.')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

import os
import re
import requests
# import webbrowser

from PIL import Image
from io import BytesIO
from mtlogger import logger
from mtprompt import Prompt

from _common import process_parent_folder, save_resized_image

IMAGE_URL = "https://tinfoil.media/ti/{game_id}/256/256/"

def main():
  process_parent_folder(process_folder)

def process_folder(folder_path):
  match = re.match(r'(^[0-9A-F]+$)', os.path.basename(os.path.normpath(folder_path)).upper())

  if match:
    game_id = match.group(1)
  else:
    logger.error(f'Could not extract a valid game ID from "{folder_path}"')
    return

  download_game_cover(game_id, folder_path)

def download_game_cover(game_id, folder_path):
  image_url = IMAGE_URL.format(game_id = game_id)
  # webbrowser.open(image_url)
  response = requests.get(image_url)

  if response.status_code != 200:
    logger.error(f'Could not access the search results for {game_id}. Status code: {response.status_code}')
    return

  img = Image.open(BytesIO(response.content))
  save_resized_image(img, folder_path)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enterToExit()

import os
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from _common import process_parent_folder, save_resized_image

TITLE_URL = 'https://serialstation.com/titles/{game_id}'

def main():
  process_parent_folder(process_folder)

def process_folder(folder_path):
  game_id = os.path.basename(os.path.normpath(folder_path))
  download_game_cover(game_id, folder_path)

def download_game_cover(game_id, folder_path):
  url = TITLE_URL.format(game_id=re.sub(r'([A-Za-z]+)(\d+)', r'\1/\2', game_id))

  response = requests.get(url)
  if response.status_code != 200:
    print(f'Failed to access {url}. Status code: {response.status_code}')
    return

  soup = BeautifulSoup(response.text, 'html.parser')
  image_tag = soup.select_one('.wp-post-image')
  if not (image_tag and 'src' in image_tag.attrs):
    print(f'Cover image not found for game ID {game_id}.')
    return

  image_url = image_tag['src']
  image_response = requests.get(image_url)
  if image_response.status_code != 200:
    print(f'Failed to download image from {image_url}.')
    return

  img = Image.open(BytesIO(image_response.content))
  save_resized_image(img, folder_path)
  print(f'Successfully processed game ID {game_id}.')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('Press Enter to exit...')
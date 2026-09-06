
import argparse
import os
import requests

from mtfs import write_json_file
from mtlogger import logger
from mtprompt import Prompt

from _constants import OUTPUT_DIR_PATH, STEAM_REQUEST_TIMEOUT, STEAM_USER_ID3, STEAM_USER_ID64

ENDPOINT_URL = 'https://api.steampowered.com/IWishlistService/GetWishlist/v1/'
OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR_PATH, STEAM_USER_ID3, 'wishlist.json')

def main():
  logger.log('Exporting Steam wishlist...')
  wishlist = get_wishlist(STEAM_USER_ID64)
  write_json_file(OUTPUT_FILE_PATH, wishlist)
  print(f'Exported {len(wishlist)} wishlist items to {OUTPUT_FILE_PATH}')
  logger.success(f'Exported {OUTPUT_FILE_PATH}.')

def get_wishlist(steam_user_id: str):
  response = requests.get(
    ENDPOINT_URL,
    params={ 'steamid': steam_user_id },
    timeout=STEAM_REQUEST_TIMEOUT,
  )
  response.raise_for_status()
  return response.json().get('response', {}).get('items', [])

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

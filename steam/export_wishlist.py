import json
import os

from mtfs import write_json_file
from mtlogger import logger
from mtprompt import Prompt

from _common import send_request
from _constants import GET_WISHLIST_ENDPOINT_URL, GET_WISHLIST_SORTED_FILTERED_ENDPOINT_URL, OUTPUT_DIR_PATH, STEAM_USER_ID3, STEAM_USER_ID64

OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR_PATH, STEAM_USER_ID3, 'wishlist.json')
PAGE_SIZE = 65535

def main():
  logger.log('Exporting Steam wishlist...')
  wishlist = get_wishlist_sorted_filtered(STEAM_USER_ID64)
  write_json_file(OUTPUT_FILE_PATH, wishlist)
  logger.success(f'Saved {len(wishlist)} wishlist items to {OUTPUT_FILE_PATH}')

def get_wishlist(steam_user_id: str):
  return send_request(
    GET_WISHLIST_ENDPOINT_URL,
    {'steamid': steam_user_id},
  ).get('items', [])

def get_wishlist_sorted_filtered(steam_user_id: str):
  return send_request(
    GET_WISHLIST_SORTED_FILTERED_ENDPOINT_URL,
    {'input_json': json.dumps({
      'steamid': steam_user_id,
      'context': {
        'language': 'english',
        'country_code': 'US',
      },
      'data_request': {},
      'filters': {},
      'share_token': '',
      'start_index': 0,
      'page_size': PAGE_SIZE,
    })},
  ).get('items', [])

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout = True)

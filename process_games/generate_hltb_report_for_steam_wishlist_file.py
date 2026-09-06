import sys

from mtfs import read_json_file
from mtlogger import logger
from mtprompt import Prompt

from _common_hltb import generate_hltb_scan_for_game_names
from _constants import HLTB_DB_PATH

OUTPUT_FILENAME = 'hltb_steam_wishlist_report.md'

def main():
  logger.log('Running HowLongToBeat scan...')

  wishlist_json_path = sys.argv[1] if len(sys.argv) > 1 else Prompt.str('Enter the path to the steam wishlist JSON file')

  wishlist_content = read_json_file(wishlist_json_path) or []
  app_names = [app_name for app in wishlist_content if (app_name := get_app_name(app))]
  db = read_json_file(HLTB_DB_PATH) or {}
  generate_hltb_scan_for_game_names(app_names, db, OUTPUT_FILENAME)

def get_app_name(app: dict):
  store_item = (app or {}).get('store_item')
  if not store_item:
    return None

  app_name = store_item.get('name')
  if not app_name:
    return None

  return app_name

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

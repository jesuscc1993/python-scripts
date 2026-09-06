import os

from mtfs import write_json_file
from mtlogger import logger
from mtprompt import Prompt
from natsort import natsorted

from _common import get_owned_games
from _constants import OUTPUT_DIR_PATH, STEAM_API_KEY, STEAM_USER_ID3, STEAM_USER_ID64

OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR_PATH, STEAM_USER_ID3, 'owned_app_ids.json')

# filters
PLAYED = None
WITH_STATS = None

def main():
  logger.log('Exporting owned Steam app IDs...')
  games = get_owned_games(STEAM_API_KEY, STEAM_USER_ID64)
  filtered_app_ids = natsorted(game['appid'] for game in games if filter_game(game))
  write_json_file(OUTPUT_FILE_PATH, filtered_app_ids)
  logger.success(f'Saved {len(filtered_app_ids)} app IDs to {OUTPUT_FILE_PATH}')

def filter_game(
  game: dict,
):
  if PLAYED is not None:
    played = game.get('playtime_forever', 0) > 0
    if played != PLAYED:
      return False
  if WITH_STATS is not None:
    has_stats = bool(game.get('has_community_visible_stats'))
    if has_stats != WITH_STATS:
      return False
  return True

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout = True)

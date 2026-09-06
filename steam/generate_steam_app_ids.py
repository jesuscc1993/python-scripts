import os
import requests

from mtfs import write_json_file
from mtlogger import logger
from mtprompt import Prompt
from natsort import natsorted

from _constants import OUTPUT_DIR_PATH, STEAM_API_KEY, STEAM_REQUEST_TIMEOUT, STEAM_USER_ID3, STEAM_USER_ID64

OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR_PATH, STEAM_USER_ID3, 'app_ids.json')

# filters
PLAYED = None
WITH_STATS = None

def main():
  logger.log('Generating Steam app IDs...')
  games = get_owned_games(STEAM_API_KEY, STEAM_USER_ID64)
  filtered_app_ids = natsorted(game['appid'] for game in games if filter_game(game))
  write_json_file(OUTPUT_FILE_PATH, filtered_app_ids)
  logger.success(f'Generated {OUTPUT_FILE_PATH}.')

def get_owned_games(
  api_key: str,
  steam_id: str,
):
  response = requests.get(
    'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/',
    params={
      'key': api_key,
      'steamid': steam_id,
      'include_appinfo': 'true',
    },
    timeout=STEAM_REQUEST_TIMEOUT,
  )
  response.raise_for_status()
  return response.json().get('response', {}).get('games', [])

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

  Prompt.enter_to_exit()

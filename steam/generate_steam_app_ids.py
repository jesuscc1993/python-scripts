import os
import requests

from dotenv import load_dotenv
from mtfs import write_json_file
from natsort import natsorted

from _constants import OUTPUT_DIR_PATH

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

STEAM_API_KEY = os.environ.get('STEAM_API_KEY')
STEAM_USER_ID3 = os.environ.get('STEAM_USER_ID3')

OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR_PATH, 'app-ids.json')

# filters
PLAYED = None
WITH_STATS = None

def main():
  games = get_owned_games(STEAM_API_KEY, STEAM_USER_ID3)
  filtered_app_ids = natsorted(game['appid'] for game in games if filter_game(game))
  write_json_file(OUTPUT_FILE_PATH, filtered_app_ids)

def get_owned_games(
  api_key: str,
  steam_id: str,
):
  url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=true'
  return requests.get(url).json().get('response', {}).get('games', [])

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

main()

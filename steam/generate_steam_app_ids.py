import json
import os
import requests

from _env import steam_api_key, steam_user_id

OUTPUT_PATH = './output'
OUTPUT_FILE = os.path.join(OUTPUT_PATH, 'app-ids.json')

# filters
PLAYED = None
WITH_STATS = None

def main():
  games = get_owned_games(steam_api_key, steam_user_id)
  filtered_app_ids = sorted(game['appid'] for game in games if filter_game(game))

  os.makedirs(OUTPUT_PATH, exist_ok = True)
  with open(OUTPUT_FILE, 'w') as f:
    json.dump(filtered_app_ids, f, indent = 2)

def get_owned_games(api_key, steam_id):
  url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=true'
  return requests.get(url).json().get('response', {}).get('games', [])

def filter_game(game):
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

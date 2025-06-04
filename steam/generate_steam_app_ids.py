import json
import os
import requests

from _env import steam_api_key, steam_user_id

OUTPUT_PATH = './output'
OUTPUT_FILE = os.path.join(OUTPUT_PATH, 'app-ids.json')

url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={steam_api_key}&steamid={steam_user_id}&include_appinfo=true'
response = requests.get(url).json()
games = response.get('response', {}).get('games', [])
app_ids = sorted([game['appid'] for game in games])

os.makedirs(OUTPUT_PATH, exist_ok = True)
with open(OUTPUT_FILE, 'w') as f:
  json.dump(app_ids, f, indent = 2)

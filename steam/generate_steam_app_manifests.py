import os
import re
import requests

from mtlogger import logger
from mtprompt import Prompt
from pathlib import Path

from _env import steam_api_key, steam_user_id

APP_MANIFEST_TEMPLATE = '''"AppState"
{{
  "appid"               "{app_id}"
  "Universe"            "1"
  "name"                "{name}"
  "StateFlags"          "4"
  "installdir"          "{install_dir}"
  "LastUpdated"         "0"
  "UpdateResult"        "0"
  "SizeOnDisk"          "0"
  "buildid"             "0"
  "LastOwner"           "{steam_user_id}"
  "BytesToDownload"     "0"
  "BytesDownloaded"     "0"
  "AutoUpdateBehavior"  "0"
  "AllowOtherDownloadsWhileRunning"  "0"
  "UserConfig"
  {{
    "language"          "english"
    "DisabledDLC"       ""
  }}
  "MountedConfig"
  {{
    "language"          "english"
  }}
}}'''

def main():
  folder = Prompt.dir(
    'Enter the path of your steam games folder'
  )

  game_folders = [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]
  if not game_folders:
    logger.log('No game folders found.')
    return

  owned_games = {sanitize_name(g['name']): g['appid'] for g in get_owned_games(steam_api_key, steam_user_id)}

  drive = Path(folder).drive
  steam_apps_path = os.path.join(drive, 'SteamLibrary', 'steamapps')
  os.makedirs(steam_apps_path, exist_ok = True)

  for game in game_folders:
    sanitized = sanitize_name(game)
    app_id = owned_games.get(sanitized)
    if not app_id:
      logger.warn(f'Skipping "{game}": no matching Steam appid found.')
      continue

    filepath = os.path.join(steam_apps_path, f'appmanifest_{app_id}.acf')
    if os.path.exists(filepath):
      logger.dim(f'Skipping "{game}": Manifest already exists ({filepath}).')
      continue

    name = game
    install_dir = game
    content = APP_MANIFEST_TEMPLATE.format(
      app_id = app_id,
      name = name,
      install_dir = install_dir,
      steam_user_id = steam_user_id
    )

    with open(filepath, 'w', encoding = 'utf-8') as f:
      f.write(content)
      logger.log(f'Created manifest for "{game}" -> {filepath}')

def get_owned_games(api_key, steam_id):
  url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=true'
  return requests.get(url).json().get('response', {}).get('games', [])

def sanitize_name(name):
  return re.sub(r'[^a-zA-Z0-9 _\-]', '', name).strip().lower()

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enter_to_exit()

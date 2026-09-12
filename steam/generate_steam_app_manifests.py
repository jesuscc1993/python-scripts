import os
import re

from mtlogger import logger
from mtfs import write_text_file
from mtprompt import Prompt
from pathlib import Path

from _common import get_owned_games
from _constants import STEAM_API_KEY, STEAM_USER_ID3, STEAM_USER_ID64

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

  owned_games = {sanitize_name(g['name']): g['appid'] for g in get_owned_games(STEAM_API_KEY, STEAM_USER_ID64)}

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
      logger.trace(f'Skipping "{game}": "({filepath})" already exists.')
      continue

    name = game
    install_dir = game
    content = APP_MANIFEST_TEMPLATE.format(
      app_id = app_id,
      name = name,
      install_dir = install_dir,
      steam_user_id = STEAM_USER_ID3
    )

    write_text_file(filepath, content)
    logger.log(f'Created manifest for "{game}" -> {filepath}')

def sanitize_name(
  name: str,
):
  return re.sub(r'[^a-zA-Z0-9 _\-]', '', name).strip().lower()

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

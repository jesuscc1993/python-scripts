import glob
import os
import re
import sys

from mtlogger import logger
from mtprompt import Prompt

DRIVES = ['D:/', 'E:/', 'Z:/']
LIBRARY_DIR = 'SteamLibrary'
STEAM_PROTOCOL = 'steam://rungameid/{app_id}'

CHARS_TO_REPLACE = re.compile(r'\s*:\s*|[<>"/\\|?*]')
CHARS_TO_REMOVE = re.compile(r'[™]')

VDF_LIBRARY_PATH = os.path.join(LIBRARY_DIR, 'libraryfolder.vdf')
VDF_TOKEN_REGEXP = re.compile(r'\{|\}|"((?:\\.|[^"\\])*)"')

def main():
  out_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir(
    'Enter the path to the directory where shortcuts will be saved'
  )

  library_paths = find_library_paths()
  if not library_paths:
    logger.warn('No Steam library folders found.')
    return

  games = find_games(library_paths)
  if not games:
    logger.warn('No installed Steam games found.')
    return

  generate_shortcuts(games, out_dir)
  logger.success(f'Generated {len(games)} shortcut(s) in "{out_dir}"')

def find_library_paths():
  library_paths = []
  for drive in DRIVES:
    vdf_path = os.path.join(drive, VDF_LIBRARY_PATH)
    if os.path.isfile(vdf_path):
      library_paths.append(os.path.join(drive, LIBRARY_DIR))

  return library_paths

def find_games(
  library_paths: list,
):
  games = []
  for library_path in library_paths:
    steam_apps_path = os.path.join(library_path, 'steamapps')
    for manifest_path in glob.glob(os.path.join(steam_apps_path, 'appmanifest_*.acf')):
      game = parse_manifest(manifest_path)
      if game:
        games.append(game)

  return games

def parse_manifest(
  manifest_path: str,
):
  state = parse_vdf(manifest_path).get('AppState', {})
  app_id = state.get('appid')
  name = state.get('name')
  if not app_id or not name:
    logger.warn(f'Skipping incomplete manifest: "{manifest_path}"')
    return None

  return {'app_id': app_id, 'name': name}

def generate_shortcuts(
  games: list,
  out_dir: str,
):
  os.makedirs(out_dir, exist_ok = True)
  for game in games:
    generate_game_shortcut(game, out_dir)

def generate_game_shortcut(
  game: dict,
  out_dir: str,
):
  try:
    name = game['name'].replace(':', '꞉')
    name = CHARS_TO_REPLACE.sub(' - ', name)
    name = CHARS_TO_REMOVE.sub('', name)
    shortcut_path = os.path.join(out_dir, name + '.url')

    with open(shortcut_path, 'w', encoding = 'utf-8') as f:
      f.write('\n'.join([
        '[InternetShortcut]',
        f'URL={STEAM_PROTOCOL.format(app_id = game["app_id"])}',
      ]))

    logger.success(f'Created shortcut for "{shortcut_path}"')

  except Exception as ex:
    logger.error(f'Failed to create shortcut for "{game["name"]}":\n{ex}')

def parse_vdf(
  vdf_path: str,
):
  with open(vdf_path, encoding = 'utf-8', errors = 'ignore') as f:
    tokens = tokenize_vdf(f.read())

  root, _ = parse_object(tokens)
  return root

def tokenize_vdf(
  text: str,
):
  tokens = []
  for match in VDF_TOKEN_REGEXP.finditer(text):
    tokens.append(match.group(0) if match.group(0) in ('{', '}') else match.group(1))
  return tokens

def parse_object(
  tokens: list,
  offset = 0,
):
  obj = {}

  while offset < len(tokens):
    token = tokens[offset]
    if token == '}':
      return obj, offset + 1

    key = token
    offset += 1

    if tokens[offset] == '{':
      value, offset = parse_object(tokens, offset + 1)
    else:
      value = tokens[offset]
      offset += 1

    obj[key] = value

  return obj, offset

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()
import os
import winsound

from dotenv import load_dotenv
from mtlogger import logger
from mtprompt import Prompt

from _common import link_dir, run_as_admin

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

USER_PROFILE = os.environ.get('UserProfile')
PROGRAM_FILES = os.environ.get('ProgramFiles')
LOCAL_DATA = os.path.join(USER_PROFILE, 'AppData', 'Local')

EPIC_USER_ID = os.environ.get('EPIC_USER_ID')
STEAM_USER_ID3 = os.environ.get('STEAM_USER_ID3')
UBISOFT_USER_ID = os.environ.get('UBISOFT_USER_ID')
GAME_CLIENTS_SAVES_PATH = os.environ.get('GAME_CLIENTS_SAVES_PATH')

DRIVES = ['D:\\', 'E:\\', 'Z:\\']

CLIENTS = os.path.join('Games', 'Clients')
GAMES = os.path.join('Games', 'PC')

STEAM_APPS = os.path.join('SteamLibrary', 'steamapps')
STEAM_APPS_COMMON = os.path.join(STEAM_APPS, 'common')

AMAZON_GAMES = 'Amazon Games'
AMAZON_LIBRARY = os.path.join(AMAZON_GAMES, 'Library')

def main():
  logger.log('Creating game client symlinks...\n')
  link_steam()
  link_amazon()
  link_epic()
  link_ubisoft()
  link_electronic_arts()
  logger.info('Finished creating game client symlinks')

def link_steam():
  if STEAM_USER_ID3:
    link_dir(
      os.path.join('D:\\', CLIENTS, 'Steam', 'steamapps'),
      os.path.join('D:\\', STEAM_APPS)
    )
    link_dir(
      os.path.join('D:\\', CLIENTS, 'Steam', 'userdata', STEAM_USER_ID3, 'config', 'grid'),
      os.path.join('Z:\\', 'Images', 'Covers', 'Steam', '_output')
    )
    for drive in DRIVES:
      link_dir(
        os.path.join(drive, STEAM_APPS_COMMON),
        os.path.join(drive, GAMES)
      )
      link_dir(
        os.path.join(drive, CLIENTS, 'Steam', 'userdata', STEAM_USER_ID3),
        os.path.join(GAME_CLIENTS_SAVES_PATH, 'Steam')
      )
    link_dir(
      os.path.join(PROGRAM_FILES, 'Steam', 'userdata', STEAM_USER_ID3),
      os.path.join(GAME_CLIENTS_SAVES_PATH, 'Steam')
    )
    print()
  else:
    logger.warn('STEAM_USER_ID3 not set. Skipping Steam links.')

def link_amazon():
  link_dir(
    os.path.join(LOCAL_DATA, AMAZON_GAMES),
    os.path.join('D:\\', CLIENTS, AMAZON_GAMES)
  )
  link_dir(
    os.path.join(LOCAL_DATA, AMAZON_LIBRARY),
    os.path.join('D:\\', GAMES)
  )
  for drive in DRIVES:
    link_dir(
      os.path.join(drive, AMAZON_LIBRARY),
      os.path.join(drive, GAMES)
    )
  print()

def link_epic():
  if EPIC_USER_ID:
    link_dir(
      os.path.join(LOCAL_DATA, 'EpicGamesLauncher', 'Saved', 'Saves', EPIC_USER_ID),
      os.path.join(GAME_CLIENTS_SAVES_PATH, 'Epic')
    )
    print()
  else:
    logger.warn('EPIC_USER_ID not set. Skipping Epic links.')

def link_ubisoft():
  if UBISOFT_USER_ID:
    link_dir(
      os.path.join('D:\\', CLIENTS, 'Uplay', 'games'),
      os.path.join('D:\\', GAMES)
    )
    link_dir(
      os.path.join('E:\\', CLIENTS, 'Uplay', 'savegames', UBISOFT_USER_ID),
      os.path.join(GAME_CLIENTS_SAVES_PATH, 'Ubisoft')
    )
  else:
    logger.warn('UBISOFT_USER_ID not set. Skipping Ubisoft links.')
  print()

def link_electronic_arts():
  link_dir(
    os.path.join(PROGRAM_FILES, 'Electronic Arts', 'EA Desktop', 'EA Desktop'),
    os.path.join('D:\\', CLIENTS, 'EA Desktop')
  )
  print()

if __name__ == '__main__':
  try:
    run_as_admin()
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  winsound.MessageBeep()
  Prompt.enter_to_exit()

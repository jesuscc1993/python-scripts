import os

from dotenv import load_dotenv
from mtlogger import logger
from mtprompt import Prompt

from _common import link_dir, run_as_admin

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

USER_PROFILE = os.environ.get('UserProfile')
DOCUMENTS = os.path.join(USER_PROFILE, 'Documents')
LOCAL_DATA = os.path.join(USER_PROFILE, 'AppData', 'Local')

GAME_SAVES_PATH = os.environ.get('GAME_SAVES_PATH')
OTHER_SAVES = os.path.join(GAME_SAVES_PATH, 'Other')
PUBLISHER_SAVES = os.path.join(GAME_SAVES_PATH, 'Publishers')

def main():
  logger.log('Creating game client symlinks...\n')
  link_user_profile()
  link_local_data()
  link_documents()
  logger.info('Finished creating game client symlinks')

def link_user_profile():
  link_dir(
    os.path.join(USER_PROFILE, 'Saved Games'),
    OTHER_SAVES
  )
  link_dir(
    os.path.join(DOCUMENTS, 'SavedGames'),
    OTHER_SAVES
  )
  print()

def link_local_data():
  link_dir(
    os.path.join(LOCAL_DATA, 'BANDAI NAMCO Entertainment'),
    os.path.join(PUBLISHER_SAVES, 'BANDAI NAMCO')
  )
  link_dir(
    os.path.join(LOCAL_DATA, 'Daedalic Entertainment GmbH'),
    os.path.join(PUBLISHER_SAVES, 'Daedalic Entertainment')
  )
  print()

def link_documents():
  link_dir(
    os.path.join(DOCUMENTS, 'My Games'),
    OTHER_SAVES
  )
  link_dir(
    os.path.join(DOCUMENTS, 'BioWare'),
    os.path.join(PUBLISHER_SAVES, 'BioWare')
  )
  link_dir(
    os.path.join(DOCUMENTS, 'EA Games'),
    os.path.join(PUBLISHER_SAVES, 'Electronic Arts')
  )
  link_dir(
    os.path.join(DOCUMENTS, 'Electronic Arts'),
    os.path.join(PUBLISHER_SAVES, 'Electronic Arts')
  )
  link_dir(
    os.path.join(DOCUMENTS, 'Electrontic Arts'),
    os.path.join(PUBLISHER_SAVES, 'Electronic Arts')
  )
  link_dir(
    os.path.join(DOCUMENTS, 'KoeiTecmo'),
    os.path.join(PUBLISHER_SAVES, 'KoeiTecmo')
  )
  print()

if __name__ == '__main__':
  try:
    run_as_admin()
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

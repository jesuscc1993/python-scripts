import os
import winsound

from dotenv import load_dotenv
from mtlogger import logger
from mtprompt import Prompt

from _common import link_dir, run_as_admin

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

APP_DATA = os.environ.get('AppData')
USER_PROFILE = os.environ.get('UserProfile')

EMULATORS_PATH = os.environ.get('EMULATORS_PATH')
EMULATORS_SAVE_PATH = os.environ.get('EMULATORS_SAVE_PATH')
ROMS_PATH = os.environ.get('ROMS_PATH')
TEXTURE_PACKS_PATH = os.environ.get('TEXTURE_PACKS_PATH')

CITRA_USER = os.path.join(EMULATORS_PATH, '3DS', '_user_')
DOLPHIN_USER = os.path.join(EMULATORS_PATH, 'Wii - GCN', '_user_')
SWITCH_USER = os.path.join(EMULATORS_PATH, 'Switch', '_user_')

def main():
  logger.log('Creating emulator symlinks...\n')
  link_yuzu()
  link_citra()
  link_ryujinx()
  link_dolphin()
  link_texture_packs()
  link_saves()
  logger.info('Finished creating emulator symlinks')

def link_yuzu():
  link_dir(
    os.path.join(APP_DATA, 'Yuzu'),
    SWITCH_USER
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'Switch', 'yuzu-early-access', 'user'),
    SWITCH_USER
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'Switch', 'Eden', 'user'),
    SWITCH_USER
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'yuzu', 'user', 'nand', 'user', 'Contents', 'registered'),
    os.path.join(ROMS_PATH, 'Switch', 'nca')
  )
  print()

def link_citra():
  link_dir(
    os.path.join(APP_DATA, 'Citra'),
    CITRA_USER
  )
  link_dir(
    os.path.join(APP_DATA, 'Azahar'),
    CITRA_USER
  )
  link_dir(
    os.path.join(EMULATORS_PATH, '3DS', 'citra-nightly', 'user'),
    CITRA_USER
  )
  link_dir(
    os.path.join(EMULATORS_PATH, '3DS', 'Azahar', 'user'),
    CITRA_USER
  )
  print()

def link_ryujinx():
  link_dir(
    os.path.join(APP_DATA, 'Ryujinx'),
    os.path.join(EMULATORS_PATH, 'Switch', 'Ryujinx')
  )
  print()

def link_dolphin():
  link_dir(
    os.path.join(EMULATORS_PATH, 'Wii - GCN', 'Dolphin', 'User'),
    DOLPHIN_USER
  )
  print()

def link_texture_packs():
  link_dir(
    os.path.join(CITRA_USER, 'load', 'textures'),
    os.path.join(TEXTURE_PACKS_PATH, '3DS')
  )
  link_dir(
    os.path.join(DOLPHIN_USER, 'Load', 'Textures'),
    os.path.join(TEXTURE_PACKS_PATH, 'Wii')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'PSP', 'PPSSPP', 'memstick', 'PSP', 'TEXTURES'),
    os.path.join(TEXTURE_PACKS_PATH, 'PSP')
  )
  print()

def link_saves():
  link_dir(
    os.path.join(USER_PROFILE, 'Documents', 'DuckStation', 'memcards'),
    os.path.join(EMULATORS_SAVE_PATH, 'PS1')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, '3DS', '_user_', 'sdmc', 'Nintendo 3DS', '00000000000000000000000000000000', '00000000000000000000000000000000', 'title', '00040000'),
    os.path.join(EMULATORS_SAVE_PATH, '3DS')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'NDS', 'DesMuMe', 'Battery'),
    os.path.join(EMULATORS_SAVE_PATH, 'NDS')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'PS2', 'PCSX2', 'memcards', 'Uncompressed.ps2'),
    os.path.join(EMULATORS_SAVE_PATH, 'PS2')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'PS3', 'RPCS3', 'dev_hdd0', 'home', '00000001', 'SAVEDATA'),
    os.path.join(EMULATORS_SAVE_PATH, 'PS3')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'PSP', 'PPSSPP', 'memstick', 'PSP', 'SAVEDATA'),
    os.path.join(EMULATORS_SAVE_PATH, 'PSP')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'Switch', '_user_', 'nand', 'user', 'save', '0000000000000000'),
    os.path.join(EMULATORS_SAVE_PATH, 'Switch')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'Wii - GCN', '_user_', 'GC', 'EUR', 'Card A'),
    os.path.join(EMULATORS_SAVE_PATH, 'GCN')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'Wii - GCN', '_user_', 'GC', 'JAP', 'Card A'),
    os.path.join(EMULATORS_SAVE_PATH, 'GCN')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'Wii - GCN', '_user_', 'GC', 'USA', 'Card A'),
    os.path.join(EMULATORS_SAVE_PATH, 'GCN')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'Wii - GCN', '_user_', 'Wii', 'title', '00010000'),
    os.path.join(EMULATORS_SAVE_PATH, 'Wii')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'Wii U', 'Cemu', 'mlc01', 'usr', 'save', '00050000'),
    os.path.join(EMULATORS_SAVE_PATH, 'Wii U')
  )
  link_dir(
    os.path.join(EMULATORS_PATH, 'X360', 'Xenia', 'content'),
    os.path.join(EMULATORS_SAVE_PATH, 'X360')
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

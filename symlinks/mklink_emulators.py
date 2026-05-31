import os
import winsound

from mtlogger import logger
from mtprompt import Prompt

from _common import link_dir, run_as_admin

USERPROFILE = os.environ.get('USERPROFILE')

CONSOLE = os.path.join('Z:\\', 'Games', 'Console')
EMULATORS = os.path.join(CONSOLE, '- Emulators -')

SAVES = os.path.join('E:\\', 'Saves', 'Consoles')
TEXTURE_PACKS = os.path.join('Z:\\', 'Projects', 'texture-packs')

def main():
  logger.log('Creating emulator symlinks...\n')

  # YUZU
  SWITCH_USER = os.path.join(EMULATORS, 'Switch', '_user_')
  APPDATA = os.environ.get('APPDATA')
  link_dir(
    os.path.join(APPDATA, 'Yuzu'),
    SWITCH_USER
  )
  link_dir(
    os.path.join(EMULATORS, 'Switch', 'yuzu-early-access', 'user'),
    SWITCH_USER
  )
  link_dir(
    os.path.join(EMULATORS, 'Switch', 'Eden', 'user'),
    SWITCH_USER
  )
  link_dir(
    os.path.join(EMULATORS, 'yuzu', 'user', 'nand', 'user', 'Contents', 'registered'),
    os.path.join(CONSOLE, 'Switch', 'nca')
  )

  # CITRA
  CITRA_USER = os.path.join(EMULATORS, '3DS', '_user_')
  link_dir(
    os.path.join(APPDATA, 'Citra'),
    CITRA_USER
  )
  link_dir(
    os.path.join(APPDATA, 'Azahar'),
    CITRA_USER
  )
  link_dir(
    os.path.join(EMULATORS, '3DS', 'citra-nightly', 'user'),
    CITRA_USER
  )
  link_dir(
    os.path.join(EMULATORS, '3DS', 'Azahar', 'user'),
    CITRA_USER
  )

  # RYUJINX
  link_dir(
    os.path.join(APPDATA, 'Ryujinx'),
    os.path.join(EMULATORS, 'Switch', 'Ryujinx')
  )

  # DOLPHIN
  DOLPHIN_USER = os.path.join(EMULATORS, 'Wii - GCN', '_user_')
  link_dir(
    os.path.join(EMULATORS, 'Wii - GCN', 'Dolphin', 'User'),
    DOLPHIN_USER
  )

  # TEXTURES
  link_dir(
    os.path.join(CITRA_USER, 'load', 'textures'),
    os.path.join(TEXTURE_PACKS, '3DS')
  )
  link_dir(
    os.path.join(DOLPHIN_USER, 'Load', 'Textures'),
    os.path.join(TEXTURE_PACKS, 'Wii')
  )
  link_dir(
    os.path.join(EMULATORS, 'PSP', 'PPSSPP', 'memstick', 'PSP', 'TEXTURES'),
    os.path.join(TEXTURE_PACKS, 'PSP')
  )

  # SAVES
  link_dir(
    os.path.join(USERPROFILE, 'Documents', 'DuckStation', 'memcards'),
    os.path.join(SAVES, 'PS1')
  )
  link_dir(
    os.path.join(EMULATORS, '3DS', '_user_', 'sdmc', 'Nintendo 3DS', '00000000000000000000000000000000', '00000000000000000000000000000000', 'title', '00040000'),
    os.path.join(SAVES, '3DS')
  )
  link_dir(
    os.path.join(EMULATORS, 'NDS', 'DesMuMe', 'Battery'),
    os.path.join(SAVES, 'NDS')
  )
  link_dir(
    os.path.join(EMULATORS, 'PS2', 'PCSX2', 'memcards', 'Uncompressed.ps2'),
    os.path.join(SAVES, 'PS2')
  )
  link_dir(
    os.path.join(EMULATORS, 'PS3', 'RPCS3', 'dev_hdd0', 'home', '00000001', 'SAVEDATA'),
    os.path.join(SAVES, 'PS3')
  )
  link_dir(
    os.path.join(EMULATORS, 'PSP', 'PPSSPP', 'memstick', 'PSP', 'SAVEDATA'),
    os.path.join(SAVES, 'PSP')
  )
  link_dir(
    os.path.join(EMULATORS, 'Switch', '_user_', 'nand', 'user', 'save', '0000000000000000'),
    os.path.join(SAVES, 'Switch')
  )
  link_dir(
    os.path.join(EMULATORS, 'Wii - GCN', '_user_', 'GC', 'EUR', 'Card A'),
    os.path.join(SAVES, 'GCN')
  )
  link_dir(
    os.path.join(EMULATORS, 'Wii - GCN', '_user_', 'GC', 'JAP', 'Card A'),
    os.path.join(SAVES, 'GCN')
  )
  link_dir(
    os.path.join(EMULATORS, 'Wii - GCN', '_user_', 'GC', 'USA', 'Card A'),
    os.path.join(SAVES, 'GCN')
  )
  link_dir(
    os.path.join(EMULATORS, 'Wii - GCN', '_user_', 'Wii', 'title', '00010000'),
    os.path.join(SAVES, 'Wii')
  )
  link_dir(
    os.path.join(EMULATORS, 'Wii U', 'Cemu', 'mlc01', 'usr', 'save', '00050000'),
    os.path.join(SAVES, 'Wii U')
  )
  link_dir(
    os.path.join(EMULATORS, 'X360', 'Xenia', 'content'),
    os.path.join(SAVES, 'X360')
  )

  logger.info('\nFinished creating emulator symlinks')

if __name__ == '__main__':
  try:
    run_as_admin()
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  winsound.MessageBeep()
  Prompt.enter_to_exit()

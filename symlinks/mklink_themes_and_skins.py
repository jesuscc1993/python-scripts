import os

from mtlogger import logger
from mtprompt import Prompt

from _common import link_dir, link_file, run_as_admin

THEMES_PATH = os.path.join('Z:\\', 'Projects', 'themes-and-skins')

RAINMETER_IN = os.path.join(THEMES_PATH, 'rainmeter')
RAINMETER_OUT = os.path.join('Z:\\', 'Software', 'Visuals', 'Rainmeter', 'Skins')

STEAM_IN = os.path.join(THEMES_PATH, 'steam')
STEAM_OUT_SFP = os.path.join('D:\\', 'Games', 'Clients', 'Steam', 'steamui')
STEAM_OUT_CSS = os.path.join('C:\\', 'Users', 'Txus', 'homebrew', 'themes')

def main():
  logger.log('Creating theme and skin symlinks...\n')
  link_rainmeter()
  link_steam()
  logger.info('Finished creating theme and skin symlinks')

def link_rainmeter():
  link_dir(
    os.path.join(RAINMETER_OUT, 'HotKey'),
    os.path.join(RAINMETER_IN, 'hotkey')
  )
  link_dir(
    os.path.join(RAINMETER_OUT, 'MetalTxus - Crystal Clear'),
    os.path.join(RAINMETER_IN, 'crystal-clear')
  )
  link_dir(
    os.path.join(RAINMETER_OUT, 'MetalTxus - Modular Game Launchers'),
    os.path.join(RAINMETER_IN, 'modular-game-launchers')
  )
  link_dir(
    os.path.join(RAINMETER_OUT, 'MetalTxus - Modular Windows 10 taskbar'),
    os.path.join(RAINMETER_IN, 'modular-windows-10-taskbar')
  )
  link_dir(
    os.path.join(RAINMETER_OUT, 'MetalTxus - Standalone'),
    os.path.join(RAINMETER_IN, 'standalone-skins')
  )
  print()

def link_steam():
  link_file(
    os.path.join(STEAM_OUT_SFP, 'libraryroot.custom.css'),
    os.path.join(STEAM_IN, 'libraryroot.custom.css')
  )
  link_file(
    os.path.join(STEAM_OUT_SFP, 'libraryroot.custom.js'),
    os.path.join(STEAM_IN, 'libraryroot.custom.js')
  )
  link_file(
    os.path.join(STEAM_OUT_SFP, 'friends.custom.css'),
    os.path.join(STEAM_IN, 'friends.custom.css')
  )
  link_file(
    os.path.join(STEAM_OUT_SFP, 'friends.custom.js'),
    os.path.join(STEAM_IN, 'friends.custom.js')
  )
  link_file(
    os.path.join(STEAM_OUT_SFP, 'webkit.css'),
    os.path.join(STEAM_IN, 'webkit.css')
  )
  link_file(
    os.path.join(STEAM_OUT_SFP, 'webkit.js'),
    os.path.join(STEAM_IN, 'webkit.js')
  )
  link_dir(
    os.path.join(STEAM_OUT_SFP, 'custom-css'),
    os.path.join(STEAM_IN, 'custom-css')
  )
  link_dir(
    os.path.join(STEAM_OUT_SFP, 'custom-js'),
    os.path.join(STEAM_IN, 'custom-js')
  )
  link_dir(
    os.path.join(STEAM_OUT_CSS, 'mt-custom-css'),
    STEAM_IN
  )
  print()

if __name__ == '__main__':
  try:
    run_as_admin()
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

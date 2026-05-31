import sys
import ctypes
import os
import winsound

from mtlogger import logger
from mtprompt import Prompt
from _common import link_dir, run_as_admin

USERPROFILE = os.environ.get('USERPROFILE')
PROGRAMFILES = os.environ.get('ProgramFiles')

LOCALDATA = os.path.join(USERPROFILE, 'AppData', 'Local')
LOCALLOWDATA = os.path.join(USERPROFILE, 'AppData', 'LocalLow')

CLIENTS = os.path.join('Games', 'Clients')
GAMES = os.path.join('Games', 'PC')

STEAMAPPS = os.path.join('SteamLibrary', 'steamapps')
STEAMAPPSCOMMON = os.path.join(STEAMAPPS, 'common')
STEAMUSERID = '137669491'

AMAZONGAMES = 'Amazon Games'
AMAZONLIBRARY = os.path.join(AMAZONGAMES, 'Library')

def main():
  logger.log('Creating game client symlinks...\n')

  # Steam
  link_dir(
    os.path.join('D:\\', CLIENTS, 'Steam', 'steamapps'),
    os.path.join('D:\\', STEAMAPPS)
  )
  link_dir(
    os.path.join('D:\\', CLIENTS, 'Steam', 'userdata', STEAMUSERID, 'config', 'grid'),
    os.path.join('Z:\\', 'Images', 'Covers', 'Steam', '_output')
  )
  link_dir(
    os.path.join('D:\\', STEAMAPPSCOMMON),
    os.path.join('D:\\', GAMES)
  )
  link_dir(
    os.path.join('E:\\', STEAMAPPSCOMMON),
    os.path.join('E:\\', GAMES)
  )
  link_dir(
    os.path.join('Z:\\', STEAMAPPSCOMMON),
    os.path.join('Z:\\', GAMES)
  )

  # Amazon
  link_dir(
    os.path.join(LOCALDATA, AMAZONGAMES),
    os.path.join('D:\\', CLIENTS, AMAZONGAMES)
  )
  link_dir(
    os.path.join(LOCALDATA, AMAZONLIBRARY),
    os.path.join('D:\\', GAMES)
  )
  os.makedirs(os.path.join('D:\\', AMAZONGAMES), exist_ok=True)
  os.makedirs(os.path.join('E:\\', AMAZONGAMES), exist_ok=True)
  os.makedirs(os.path.join('Z:\\', AMAZONGAMES), exist_ok=True)
  link_dir(
    os.path.join('D:\\', AMAZONLIBRARY),
    os.path.join('D:\\', GAMES)
  )
  link_dir(
    os.path.join('E:\\', AMAZONLIBRARY),
    os.path.join('E:\\', GAMES)
  )
  link_dir(
    os.path.join('Z:\\', AMAZONLIBRARY),
    os.path.join('Z:\\', GAMES)
  )

  # Ubisoft
  os.makedirs(os.path.join('D:\\', CLIENTS, 'Uplay'), exist_ok=True)
  link_dir(
    os.path.join('D:\\', CLIENTS, 'Uplay', 'games'),
    os.path.join('D:\\', GAMES)
  )

  # Electronic Arts
  link_dir(
    os.path.join(PROGRAMFILES, 'Electronic Arts', 'EA Desktop', 'EA Desktop'),
    os.path.join('D:\\', CLIENTS, 'EA Desktop')
  )

  logger.info('\nFinished creating game client symlinks')

if __name__ == '__main__':
  try:
    run_as_admin()
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  winsound.MessageBeep()
  Prompt.enter_to_exit()

import sys
import ctypes
import os
import winsound

from mtlogger import logger
from mtprompt import Prompt
from _common import link_dir, run_as_admin

USERPROFILE = os.environ.get('USERPROFILE')
PROGRAMFILES = os.environ.get('ProgramFiles')

DRIVES = ['D:\\', 'E:\\', 'Z:\\']

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
  link_steam()
  link_amazon()
  link_ubisoft()
  link_electronic_arts()
  logger.info('Finished creating game client symlinks')

def link_steam():
  link_dir(
    os.path.join('D:\\', CLIENTS, 'Steam', 'steamapps'),
    os.path.join('D:\\', STEAMAPPS)
  )
  link_dir(
    os.path.join('D:\\', CLIENTS, 'Steam', 'userdata', STEAMUSERID, 'config', 'grid'),
    os.path.join('Z:\\', 'Images', 'Covers', 'Steam', '_output')
  )
  for drive in DRIVES:
    link_dir(
      os.path.join(drive, STEAMAPPSCOMMON),
      os.path.join(drive, GAMES)
    )
  print()

def link_amazon():
  link_dir(
    os.path.join(LOCALDATA, AMAZONGAMES),
    os.path.join('D:\\', CLIENTS, AMAZONGAMES)
  )
  link_dir(
    os.path.join(LOCALDATA, AMAZONLIBRARY),
    os.path.join('D:\\', GAMES)
  )
  for drive in DRIVES:
    link_dir(
      os.path.join(drive, AMAZONLIBRARY),
      os.path.join(drive, GAMES)
    )
  print()

def link_ubisoft():
  link_dir(
    os.path.join('D:\\', CLIENTS, 'Uplay', 'games'),
    os.path.join('D:\\', GAMES)
  )
  print()

def link_electronic_arts():
  link_dir(
    os.path.join(PROGRAMFILES, 'Electronic Arts', 'EA Desktop', 'EA Desktop'),
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

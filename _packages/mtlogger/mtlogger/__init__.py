from colorama import init, Fore
from enum import Enum

init(autoreset = True, wrap = True, convert = True)

class LogLevel(Enum):
  DEBUG = 'DEBUG'
  ERROR = 'ERROR'
  INFO = 'INFO'
  LOG = 'LOG'
  WARN = 'WARN'

class Logger:
  def format(self, level: LogLevel, msg: str = ''):
    color = {
      LogLevel.DEBUG: Fore.CYAN,
      LogLevel.ERROR: Fore.RED,
      LogLevel.INFO: Fore.GREEN,
      LogLevel.LOG: '',
      LogLevel.WARN: Fore.YELLOW
    }.get(level, '')
    return f"{color}{msg}"

  def debug(self, msg: str = ''):
    print(self.format(LogLevel.DEBUG, msg))

  def error(self, msg: str = ''):
    print(self.format(LogLevel.ERROR, msg))

  def info(self, msg: str = ''):
    print(self.format(LogLevel.INFO, msg))

  def log(self, msg: str = ''):
    print(self.format(LogLevel.LOG, msg))

  def warn(self, msg: str = ''):
    print(self.format(LogLevel.WARN, msg))

  def unhandledError(self, msg: str = ''):
    print(self.format(LogLevel.ERROR, f'Unhandled error: {msg}'))

logger = Logger()

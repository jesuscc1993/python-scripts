from colorama import init, Fore, Style
from enum import Enum

init(autoreset = True, wrap = True, convert = True)

class LogLevel(Enum):
  DEBUG = 'DEBUG'
  ERROR = 'ERROR'
  INFO = 'INFO'
  LOG = 'LOG'
  WARN = 'WARN'

class Logger:
  def formatLevel(self, level: LogLevel, msg: str = ''):
    color = {
      LogLevel.DEBUG: Fore.CYAN,
      LogLevel.ERROR: Fore.RED,
      LogLevel.INFO: Fore.GREEN,
      LogLevel.LOG: '',
      LogLevel.WARN: Fore.YELLOW
    }.get(level, '')
    return self.colorize(color, msg)

  def colorize(_, color: str, msg: str = ''):
    return f"{color}{msg}{Fore.RESET}"

  # classic functions

  def debug(self, msg: str = ''):
    print(self.formatLevel(LogLevel.DEBUG, msg))

  def error(self, msg: str = ''):
    print(self.formatLevel(LogLevel.ERROR, msg))

  def info(self, msg: str = ''):
    print(self.formatLevel(LogLevel.INFO, msg))

  def log(self, msg: str = ''):
    print(self.formatLevel(LogLevel.LOG, msg))

  def warn(self, msg: str = ''):
    print(self.formatLevel(LogLevel.WARN, msg))

  # functions with icons

  def success(self, msg: str = ''):
    print(f'{self.colorize(Fore.GREEN, "✓")} {msg}')

  def failure(self, msg: str = ''):
    print(f'{self.colorize(Fore.RED, "✗")} {msg}')

  # other functions

  def dim(self, msg: str = ''):
    print(self.colorize(Fore.LIGHTBLACK_EX, msg))

  def unhandledError(self, msg: str = ''):
    print(self.formatLevel(LogLevel.ERROR, f'Unhandled error: {msg}'))

logger = Logger()

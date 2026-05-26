import os

from colorama import init, Fore, Style
from enum import Enum
from typing import Optional, TypedDict, Unpack

init(autoreset = True, wrap = True, convert = True)

class LogLevel(Enum):
  DEBUG = 'DEBUG'
  ERROR = 'ERROR'
  INFO = 'INFO'
  LOG = 'LOG'
  WARN = 'WARN'

class LogOptions(TypedDict, total=False):
  prefix_newline: bool

class Logger:
  # core functions
  def formatLevel(self, level: LogLevel, msg = ''):
    color = {
      LogLevel.DEBUG: Fore.CYAN,
      LogLevel.ERROR: Fore.RED,
      LogLevel.INFO: Fore.GREEN,
      LogLevel.LOG: '',
      LogLevel.WARN: Fore.YELLOW
    }.get(level, '')
    return self.colorize(color, msg)

  def colorize(_, color: str, msg = ''):
    return f"{color}{msg}{Fore.RESET}"

  def print(_, msg = '', options: Optional[LogOptions] = None):
    prefix_newline = options.get('prefix_newline', False) if options else False
    print(f'{'\n' if prefix_newline else ''}{msg}')
  #

  # classic functions
  def debug(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatLevel(LogLevel.DEBUG, msg), LogOptions(**kwargs))

  def error(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatLevel(LogLevel.ERROR, msg), LogOptions(**kwargs))

  def info(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatLevel(LogLevel.INFO, msg), LogOptions(**kwargs))

  def log(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatLevel(LogLevel.LOG, msg), LogOptions(**kwargs))

  def warn(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatLevel(LogLevel.WARN, msg), LogOptions(**kwargs))
  #

  # functions with icons
  def success(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(f'{self.colorize(Fore.GREEN, "✓")} {msg}', LogOptions(**kwargs))

  def failure(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(f'{self.colorize(Fore.RED, "✗")} {msg}', LogOptions(**kwargs))
  #

  # other functions
  def dim(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.colorize(Fore.LIGHTBLACK_EX, msg), LogOptions(**kwargs))

  def unhandledError(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatLevel(LogLevel.ERROR, f'Unhandled error: {msg}'), LogOptions(**kwargs))

  def hr(self):
    self.dim('─' * os.get_terminal_size().columns)
  #

logger = Logger()

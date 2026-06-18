import os

from colorama import init, Fore, Style
from enum import Enum
from typing import Optional, TypedDict, Unpack

init(autoreset = True, wrap = True, convert = True)

class LogLevel(Enum):
  TRACE = 'TRACE'
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
      LogLevel.TRACE: Fore.LIGHTBLACK_EX,
      LogLevel.DEBUG: Fore.CYAN,
      LogLevel.ERROR: Fore.RED,
      LogLevel.INFO: Fore.GREEN,
      LogLevel.LOG: '',
      LogLevel.WARN: Fore.YELLOW
    }.get(level, '')
    return self.colorize(color, msg)

  def colorize(_, color: str, msg = ''):
    return f"{color}{msg.replace(Fore.RESET, color)}{Fore.RESET}"

  def print(_, msg = '', options: Optional[LogOptions] = None):
    prefix_newline = options.get('prefix_newline', False) if options else False
    print(f'{'\n' if prefix_newline else ''}{msg}')
  #

  # formatting functions
  def formatTrace(self, msg = ''):
    return self.formatLevel(LogLevel.TRACE, msg)

  def formatDebug(self, msg = ''):
    return self.formatLevel(LogLevel.DEBUG, msg)

  def formatError(self, msg = ''):
    return self.formatLevel(LogLevel.ERROR, msg)

  def formatInfo(self, msg = ''):
    return self.formatLevel(LogLevel.INFO, msg)

  def formatLog(self, msg = ''):
    return self.formatLevel(LogLevel.LOG, msg)

  def formatWarn(self, msg = ''):
    return self.formatLevel(LogLevel.WARN, msg)
  #

  # print functions
  def trace(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatTrace(msg), LogOptions(**kwargs))

  def debug(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatDebug(msg), LogOptions(**kwargs))

  def error(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatError(msg), LogOptions(**kwargs))

  def info(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatInfo(msg), LogOptions(**kwargs))

  def log(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatLog(msg), LogOptions(**kwargs))

  def warn(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatWarn(msg), LogOptions(**kwargs))
  #

  # functions with icons
  def success(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(f'{self.colorize(Fore.GREEN, "✓")} {msg}', LogOptions(**kwargs))

  def failure(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(f'{self.colorize(Fore.RED, "✗")} {msg}', LogOptions(**kwargs))
  #

  # other functions
  def unhandledError(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(self.formatError(f'Unhandled error: {msg}'), LogOptions(**kwargs))

  def hr(self):
    self.print(self.colorize(Fore.LIGHTBLACK_EX, '─' * os.get_terminal_size().columns))
  #

logger = Logger()

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

LOG_LEVEL_SEVERITY = {
  LogLevel.TRACE: 0,
  LogLevel.DEBUG: 1,
  LogLevel.LOG: 2,
  LogLevel.INFO: 2,
  LogLevel.WARN: 3,
  LogLevel.ERROR: 4,
}

class LevelColor(Enum):
  TRACE = Fore.LIGHTBLACK_EX
  DEBUG = Fore.CYAN
  ERROR = Fore.RED
  INFO = Fore.GREEN
  LOG = ''
  WARN = Fore.YELLOW

class LogOptions(TypedDict, total=False):
  prefix_newline: bool

class Logger:
  def __init__(self, level: LogLevel = LogLevel.TRACE):
    self.level = level

  # core functions
  def colorize(_, color: str, msg = ''):
    return f"{color}{msg.replace(Fore.RESET, color)}{Fore.RESET}"

  def format_level(self, level: LogLevel, msg = ''):
    return self.colorize(LevelColor[level.name].value, msg)

  def is_enabled(self, level: LogLevel):
    return LOG_LEVEL_SEVERITY[level] >= LOG_LEVEL_SEVERITY[self.level]

  def print(self, level: LogLevel, msg = '', options: Optional[LogOptions] = None):
    if not self.is_enabled(level):
      return

    prefix_newline = options.get('prefix_newline', False) if options else False
    print(f'{'\n' if prefix_newline else ''}{msg}')
  #

  # formatting functions
  def format_trace(self, msg = ''):
    return self.format_level(LogLevel.TRACE, msg)

  def format_debug(self, msg = ''):
    return self.format_level(LogLevel.DEBUG, msg)

  def format_error(self, msg = ''):
    return self.format_level(LogLevel.ERROR, msg)

  def format_info(self, msg = ''):
    return self.format_level(LogLevel.INFO, msg)

  def format_log(self, msg = ''):
    return self.format_level(LogLevel.LOG, msg)

  def format_warn(self, msg = ''):
    return self.format_level(LogLevel.WARN, msg)

  def format_success(self, msg = ''):
    return f'{self.colorize(Fore.GREEN, "✓")} {msg}'

  def format_failure(self, msg = ''):
    return f'{self.colorize(Fore.RED, "✗")} {msg}'
  #

  # print functions
  def trace(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(LogLevel.TRACE, self.format_trace(msg), LogOptions(**kwargs))

  def debug(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(LogLevel.DEBUG, self.format_debug(msg), LogOptions(**kwargs))

  def error(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(LogLevel.ERROR, self.format_error(msg), LogOptions(**kwargs))

  def info(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(LogLevel.INFO, self.format_info(msg), LogOptions(**kwargs))

  def log(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(LogLevel.LOG, self.format_log(msg), LogOptions(**kwargs))

  def warn(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(LogLevel.WARN, self.format_warn(msg), LogOptions(**kwargs))

  def success(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(LogLevel.LOG, self.format_success(msg), LogOptions(**kwargs))

  def failure(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(LogLevel.ERROR, self.format_failure(msg), LogOptions(**kwargs))
  #

  # other functions
  def unhandled_error(self, msg = '', **kwargs: Unpack[LogOptions]):
    self.print(LogLevel.ERROR, self.format_error(f'Unhandled error: {msg}'), LogOptions(**kwargs))

  def hr(self):
    self.print(LogLevel.LOG, self.colorize(Fore.LIGHTBLACK_EX, '─' * os.get_terminal_size().columns))
  #

logger = Logger()

import csv
import io
import mtsound
import os
import sys
import threading

from mtlogger import logger


def to_bool(val: str):
  val = val.strip().lower()

  if val in ('y', 'yes', 'true'):
    return True
  if val in ('n', 'no', 'false'):
    return False

  raise ValueError(f'Value "{val}" is not a valid boolean (y/n).')


def to_int(val: str):
  val = val.strip()

  try:
    return int(val)
  except ValueError:
    raise ValueError(f'Input "{val}" is not an integer.')


def to_float(val: str):
  val = val.strip()

  try:
    return float(val)
  except ValueError:
    raise ValueError(f'Input "{val}" is not a valid number.')


def to_path(val: str):
  val = os.path.abspath(val.strip(' "'))

  if not os.path.exists(val):
    raise ValueError(f'Path "{val}" does not exist.')

  return val


def to_dir(val: str):
  val = os.path.abspath(val.strip(' "'))

  if not os.path.isdir(val):
    raise ValueError(f'Path "{val}" is not a directory.')

  return val


def to_file(val: str):
  val = os.path.abspath(val.strip(' "'))

  if not os.path.isfile(val):
    raise ValueError(f'Path "{val}" is not a file.')

  return val


def to_list(val: str):
  try:
    values = next(
      csv.reader(io.StringIO(val), skipinitialspace=True, strict=True)
    )
  except csv.Error:
    raise ValueError(f'Input "{val}" is not a valid comma-separated list.')

  parsed_values = []
  for item in values:
    item = item.strip()
    if len(item) >= 2 and item[0] == item[-1] and item[0] in ('"', "'"):
      item = item[1:-1]
    parsed_values.append(item)

  return parsed_values


class Prompt:
  @staticmethod
  def str(prompt='', *, optional=False, default: str | None = None):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default))

      if not val and default is None and not optional:
        logger.error('A string is required.\n')
        continue

      logger.log()
      return val if val != '' else default

  @staticmethod
  def list(prompt='', *, optional=False, default: list | None = None):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default))

      if not val and default is None and not optional:
        logger.error('A list is required.\n')
        continue

      if val:
        try:
          val = to_list(val)
        except ValueError as ex:
          logger.error(f'{ex}\n')
          continue

      logger.log()
      return val if val else default

  @staticmethod
  def option(options: list, prompt='', *, optional=False, default=None):
    if not isinstance(options, list):
      raise TypeError('A list of options must be passed.')

    prompt = prompt.strip(' "\'')

    while True:
      full_prompt = format_prompt(prompt, default, use_colon=False)
      for i, option in enumerate(options):
        full_prompt += f'\n {i + 1} - {option}'
      full_prompt += '\n:'

      val = input(full_prompt).strip()

      if not val:
        if default is None and not optional:
          logger.error('An option is required.\n')
          continue
        logger.log()
        return default

      if not val.isdigit() or not (1 <= int(val) <= len(options)):
        logger.error(f'Input "{val}" is not a valid index.\n')
        continue

      logger.log()
      return options[int(val) - 1]

  @staticmethod
  def int(prompt='', *, optional=False, default: int | None = None):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default))

      if not val and default is None and not optional:
        logger.error('An integer is required.\n')
        continue

      if val != '':
        try:
          val = to_int(val)
        except ValueError as ex:
          logger.error(f'{ex}\n')
          continue

      logger.log()
      return val if val != '' else default

  @staticmethod
  def float(prompt='', *, optional=False, default: float | None = None):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default))

      if not val and default is None and not optional:
        logger.error('A number is required.\n')
        continue

      if val != '':
        try:
          val = to_float(val)
        except ValueError as ex:
          logger.error(f'{ex}\n')
          continue

      logger.log()
      return val if val != '' else default

  @staticmethod
  def bool(prompt: str, *, optional=False, default: bool | None = None):
    prompt = prompt.strip(' "\'')

    default_display = 'y/n'
    if default == True:
      default_display = 'Y/n'
    elif default == False:
      default_display = 'y/N'

    while True:
      val = input(f'{prompt} ({default_display})\n: ').strip()

      if not val:
        boolean = default
      else:
        try:
          boolean = to_bool(val)
        except ValueError:
          boolean = default

      if boolean is None and default is None and not optional:
        logger.error('A value is required.\n')
        continue

      logger.log()
      return boolean

  @staticmethod
  def path(
    prompt='Enter the path you want to process',
    *,
    optional=False,
    default: str = None,
  ):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default)).strip(' "')

      if not val and default is None and not optional:
        logger.error('A path is required.\n')
        continue

      if val:
        try:
          val = to_path(val)
        except ValueError as ex:
          logger.error(f'{ex}\n')
          continue

      logger.log()
      return val if val != '' else default

  @staticmethod
  def dir(
    prompt='Enter the path to the directory you want to process',
    *,
    optional=False,
    default: str = None,
  ):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default)).strip(' "')

      if not val and default is None and not optional:
        logger.error('A directory path is required.\n')
        continue

      if val:
        try:
          val = to_dir(val)
        except ValueError as ex:
          logger.error(f'{ex}\n')
          continue

      logger.log()
      return val if val != '' else default

  @staticmethod
  def file(
    prompt='Enter the path to the file you want to process',
    *,
    optional=False,
    default: str = None,
  ):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default)).strip(' "')

      if not val and default is None and not optional:
        logger.error('A file path is required.\n')
        continue

      if val:
        try:
          val = to_file(val)
        except ValueError as ex:
          logger.error(f'{ex}\n')
          continue

      logger.log()
      return val if val != '' else default

  @staticmethod
  def enter_to_exit(timeout=False, sound=True):
    if sound:
      mtsound.notify()

    if os.getenv('NO_ENTER_TO_EXIT'):
      return

    if timeout is True:
      timeout = 3

    if timeout is False or timeout is None:
      input('\nPress Enter to exit...')
      return

    entered = threading.Event()

    def wait_for_input():
      input('')
      entered.set()

    thread = threading.Thread(target=wait_for_input, daemon=True)
    thread.start()

    sys.stdout.write('\n')
    for remaining in range(timeout, 0, -1):
      sys.stdout.write(
        f'\rPress Enter to exit. Terminal will automatically close in {remaining}s...'
      )
      sys.stdout.flush()
      if entered.wait(timeout=1):
        return

    os._exit(0)


def format_prompt(prompt: str, default: str | None = None, use_colon=True):
  formatted_prompt = prompt.strip(' ')
  formatted_default = f'(default: {default})' if default else ''
  return f'{formatted_prompt}{" " if formatted_default and not formatted_prompt.endswith("\n") else ""}{formatted_default}{"\n: " if use_colon and (formatted_prompt or formatted_default) else ""}'

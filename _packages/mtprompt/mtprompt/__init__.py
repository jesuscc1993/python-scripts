import mtsound
import os
import sys
import threading

from mtenv import Env
from mtlogger import logger
from mtvalidation import (
  to_bool,
  to_dir,
  to_file,
  to_float,
  to_int,
  to_list,
  to_path,
)


class Prompt:
  PROMPT__MUTE = 'PROMPT__MUTE'
  PROMPT__NO_ENTER_TO_EXIT = 'PROMPT__NO_ENTER_TO_EXIT'

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
    if sound and not Env.bool(Prompt.PROMPT__MUTE):
      mtsound.notify()

    if Env.bool(Prompt.PROMPT__NO_ENTER_TO_EXIT):
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
  formatted_default = f'(default: {default})' if default is not None else ''
  return f'{formatted_prompt}{" " if formatted_default and not formatted_prompt.endswith("\n") else ""}{formatted_default}{"\n: " if use_colon and (formatted_prompt or formatted_default) else ""}'

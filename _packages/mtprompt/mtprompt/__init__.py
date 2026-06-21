import os
import sys
import threading
import winsound

from mtlogger import logger

class Prompt:

  @staticmethod
  def str(
    prompt = '',
    *,
    optional = False,
    default: str = None
  ):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default))

      if not val and default is None and not optional:
        logger.error('A string is required.\n')
        continue

      logger.log()
      return val if val else default

  @staticmethod
  def int(
    prompt = '',
    *,
    optional = False,
    default: int = None
  ):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default))

      if not val and default is None and not optional:
        logger.error('An integer is required.\n')
        continue

      if val != '':
        try:
          val = int(val)
        except ValueError:
          logger.error(f'Input "{val}" is not an integer.\n')
          continue

      logger.log()
      return val if val else default

  @staticmethod
  def bool(
    prompt: str,
    *,
    optional = False,
    default: bool = None
  ):
    prompt = prompt.strip(' "\'')

    default_display = 'y/n'
    if (default == True):
      default_display = 'Y/n'
    elif (default == False):
      default_display = 'y/N'

    while True:
      val = input(f'{prompt} ({default_display}):\n').strip().lower()

      if val in ('y', 'yes'):
        boolean = True
      elif val in ('n', 'no'):
        boolean = False
      else:
        boolean = default

      if boolean is None and default is None and not optional:
        logger.error('A value is required.\n')
        continue

      logger.log()
      return boolean

  @staticmethod
  def path(
    prompt = 'Enter the path you want to process',
    *,
    optional = False,
    default: str = None
  ):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default)).strip(' "')

      if not val and default is None and not optional:
        logger.error('A path is required.\n')
        continue

      if val and not os.path.exists(val):
        logger.error(f'Path "{val}" does not exist.\n')
        continue

      logger.log()
      return val if val else default

  @staticmethod
  def dir(
    prompt = 'Enter the path to the directory you want to process',
    *,
    optional = False,
    default: str = None
  ):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default)).strip(' "')

      if not val and default is None and not optional:
        logger.error('A directory path is required.\n')
        continue

      if val and not os.path.isdir(val):
        logger.error(f'Path "{val}" is not a directory.\n')
        continue

      logger.log()
      return val if val else default

  @staticmethod
  def file(
    prompt = 'Enter the path to the file you want to process',
    *,
    optional = False,
    default: str = None
  ):
    prompt = prompt.strip(' "\'')

    while True:
      val = input(format_prompt(prompt, default)).strip(' "')

      if not val and default is None and not optional:
        logger.error('A file path is required.\n')
        continue

      if val and not os.path.isfile(val):
        logger.error(f'Path "{val}" is not a file.\n')
        continue

      logger.log()
      return val if val else default

  @staticmethod
  def enter_to_exit(timeout = False, sound = True):
    if sound:
      winsound.MessageBeep()

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

    thread = threading.Thread(target = wait_for_input, daemon = True)
    thread.start()

    sys.stdout.write('\n')
    for remaining in range(timeout, 0, -1):
      sys.stdout.write(f'\rPress Enter to exit. Terminal will automatically close in {remaining}s...')
      sys.stdout.flush()
      if entered.wait(timeout = 1):
        return

    os._exit(0)

def format_prompt(prompt: str, default: str = None):
  formatted_prompt = prompt.strip(' ')
  formatted_default = f'(default: {default})' if default else ''
  return f'{formatted_prompt}{' ' if formatted_default and not formatted_prompt.endswith('\n') else ''}{formatted_default}{":\n" if formatted_prompt or formatted_default else ""}'

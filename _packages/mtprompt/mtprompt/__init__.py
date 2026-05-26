import os

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

      if not val and not optional:
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

      if not val and not optional:
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

      if boolean is None and not optional:
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

      if not val and not optional:
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

      if not val and not optional:
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

      if not val and not optional:
        logger.error('A file path is required.\n')
        continue

      if val and not os.path.isfile(val):
        logger.error(f'Path "{val}" is not a file.\n')
        continue

      logger.log()
      return val if val else default

  @staticmethod
  def enter_to_exit():
    if not os.getenv('NO_ENTER_TO_EXIT'):
      input('\nPress Enter to exit...')

def format_prompt(prompt: str, default: str = None):
  formatted_prompt = prompt.strip()
  return f'{formatted_prompt}{f" (default: {default})" if default else ""}:\n'

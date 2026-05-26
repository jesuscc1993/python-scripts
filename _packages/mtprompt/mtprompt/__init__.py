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
      string = input(f'{prompt}:\n')

      if not string and not optional:
        logger.error('A string is required.\n')
        continue

      logger.log()
      return string if string else default

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
      path = input(format_prompt(prompt, default)).strip(' "')

      if not path and not optional:
        logger.error('A path path is required.\n')
        continue

      if path and not os.path.exists(path):
        logger.error(f'Path "{path}" is not a path.\n')
        continue

      logger.log()
      return path if path else default

  @staticmethod
  def dir(
    prompt = 'Enter the path to the directory you want to process',
    *,
    optional = False,
    default: str = None
  ):
    prompt = prompt.strip(' "\'')

    while True:
      directory = input(format_prompt(prompt, default)).strip(' "')

      if not directory and not optional:
        logger.error('A directory path is required.\n')
        continue

      if directory and not os.path.isdir(directory):
        logger.error(f'Path "{directory}" is not a directory.\n')
        continue

      logger.log()
      return directory if directory else default

  @staticmethod
  def file(
    prompt = 'Enter the path to the file you want to process',
    *,
    optional = False,
    default: str = None
  ):
    prompt = prompt.strip(' "\'')

    while True:
      file = input(format_prompt(prompt, default)).strip(' "')

      if not file and not optional:
        logger.error('A file path is required.\n')
        continue

      if file and not os.path.isfile(file):
        logger.error(f'Path "{file}" is not a file.\n')
        continue

      logger.log()
      return file if file else default

  @staticmethod
  def prompt_depth(
    prompt = 'Enter the depth for processing subfolders',
    *,
    optional = False,
    default: int = 1
  ):
    while True:
      try:
        depth = int(input(format_prompt(prompt, default)).strip() or default)
        if depth < 0:
          raise ValueError()
      except ValueError:
        logger.error('Depth must be a positive integer.')
        continue

      if not depth and not optional:
        logger.error('A depth is required.\n')
        continue

      logger.log()
      return depth if depth else default

  @staticmethod
  def enter_to_exit():
    if not os.getenv('NO_ENTER_TO_EXIT'):
      input('\nPress Enter to exit...')

def format_prompt(prompt: str, default: str = None):
  formatted_prompt = prompt.strip()
  return f'{formatted_prompt}{f" (default: {default})" if default else ""}:\n'

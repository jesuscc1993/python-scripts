import os

from mtlogger import logger

class Prompt:

  @staticmethod
  def dir(
    prompt = 'Enter the path to the directory you want to process:',
    *,
    optional = False
  ):
    prompt = prompt.strip(' "\'')

    while True:
      parent_folder = input(f'{prompt}\n')

      if not parent_folder and not optional:
        logger.error('A directory path is required.')
        continue

      if parent_folder and not os.path.isdir(parent_folder):
        logger.error(f'Path "{parent_folder}" is not a directory.')
        continue

      return parent_folder if parent_folder else None

  @staticmethod
  def enterToExit():
    input('\nPress Enter to exit...')

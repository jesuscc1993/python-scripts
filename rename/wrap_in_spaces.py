import os
import sys

from mtlogger import logger
from mtprompt import Prompt, to_path


def main():
  if len(sys.argv) > 1:
    path = to_path(sys.argv[1])
  else:
    path = Prompt.path(
      'Enter the path to the file/directory you want to rename'
    )

  rename_file(path)


def rename_file(path):
  directory = os.path.dirname(path)
  name = os.path.basename(path)
  new_name = f'\u00a0{name}\u00a0'
  new_path = os.path.join(directory, new_name)

  if os.path.exists(new_path):
    raise FileExistsError(f'Path already exists: "{new_path}".')

  os.rename(path, new_path)


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

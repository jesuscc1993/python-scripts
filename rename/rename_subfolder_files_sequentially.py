import os
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import rename_items_by_sequential_pattern


def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your files'
    )

  name_pattern = Prompt.str(
    'Enter the name pattern\nUse $ for number interpolation\n', default='$'
  )

  subfolders = [
    os.path.join(parent_dir, folder_name)
    for folder_name in os.listdir(parent_dir)
    if (
      os.path.isdir(os.path.join(parent_dir, folder_name))
      and not folder_name.startswith('.')
    )
  ]

  for subfolder in subfolders:
    items = [
      file_name
      for file_name in os.listdir(subfolder)
      if (
        os.path.isfile(os.path.join(subfolder, file_name))
        and not file_name.startswith('.')
      )
    ]

    rename_items_by_sequential_pattern(subfolder, items, name_pattern)


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

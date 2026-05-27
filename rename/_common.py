import os

from mtlogger import logger
from natsort import natsorted

def rename_items_by_sequential_pattern(parent_dir, items, name_pattern):
  logger.log(f'Renaming items in "{parent_dir}"...')

  items = natsorted(items)
  num_digits = len(str(len(items)))

  for index, old_name in enumerate(items, start = 1):
    old_path = os.path.join(parent_dir, old_name)
    extension = os.path.splitext(old_name)[1] if os.path.isfile(old_path) else ''
    sequence = str(index).zfill(num_digits)
    new_name = f'{name_pattern.replace("$", sequence)}{extension}'
    new_path = os.path.join(parent_dir, new_name)

    os.rename(old_path, new_path)
    logger.debug(f'Renamed "{old_name}" to "{new_name}".')
  logger.success(f'Finished renaming items in "{parent_dir}".')

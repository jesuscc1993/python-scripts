import os

from mtlogger import logger
from natsort import natsorted

def rename_items_by_sequential_pattern(
  parent_dir_path: str,
  items: list,
  name_pattern: str,
):
  logger.log(f'Renaming items in "{parent_dir_path}"...')

  items = natsorted(items)
  num_digits = len(str(len(items)))

  for index, old_name in enumerate(items, start = 1):
    old_item_path = os.path.join(parent_dir_path, old_name)
    item_ext = os.path.splitext(old_name)[1] if os.path.isfile(old_item_path) else ''
    sequence = str(index).zfill(num_digits)
    new_item_name = f'{name_pattern.replace("$", sequence)}{item_ext}'
    new_item_path = os.path.join(parent_dir_path, new_item_name)

    os.rename(old_item_path, new_item_path)
    logger.debug(f'Renamed "{old_name}" to "{new_item_name}".')
  logger.success(f'Finished renaming items in "{parent_dir_path}".')

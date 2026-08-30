import os
import re
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import FILE_BLACKLIST, process_parent_folder

def main():
  parent_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the files you want to group')

  process_parent_folder(parent_dir, should_process_item, get_group_name)

def should_process_item(
  item_path: str,
):
  if not os.path.isfile(item_path):
    return False

  for pattern in FILE_BLACKLIST:
    if re.fullmatch(pattern, os.path.basename(item_path)):
      return False

  return True

def get_group_name(
  file_path: str,
):
  file_name = os.path.basename(file_path)
  tags = re.findall(r'\[(.*?)\]', file_name)
  tags = [tag.strip() for tag in tags if not re.fullmatch(r'\d+', tag.strip())]
  return ' '.join(f'[{tag}]' for tag in tags)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

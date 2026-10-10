import os
import re
import sys

from mtlogger import logger
from mtprompt import Prompt, to_dir

from _common import FILE_BLACKLIST, find_files_to_process, group_files


def main():
  parent_dir = (
    to_dir(sys.argv[1])
    if len(sys.argv) > 1
    else Prompt.dir(
      'Enter the path to the directory containing the files you want to group'
    )
  )

  files_to_process = find_files_to_process(parent_dir, should_process_item)
  group_files(parent_dir, files_to_process, get_group_name)


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
  filename: str,
):
  name = get_normalized_name(filename)
  if '-' in name:
    name = name[: name.rfind('-')].strip()
  name = os.path.splitext(name)[0].strip()
  name = re.sub(r'\s+', ' ', name)
  return name


def get_normalized_name(
  filename: str,
):
  name, ext = os.path.splitext(filename)
  name = re.sub(r'\[[^\]]*\]|\{[^\}]*\}', '', name)
  name = re.sub(r'\s+', ' ', name).strip()
  return f'{name}{ext}'


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

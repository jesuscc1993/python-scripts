import os
import re
import sys

from mtlogger import logger
from mtprompt import Prompt, to_dir

from _common import find_files_to_process, group_files

PROTOCOL_MAP = {
  'com.epicgames.launcher': 'Epic Games'
}

def main():
  parent_dir = to_dir(sys.argv[1]) if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the files you want to group')

  files_to_process = find_files_to_process(parent_dir, should_process_item)
  group_files(parent_dir, files_to_process, get_group_name)

def should_process_item(
  item_path: str,
):
  return os.path.isfile(item_path) and item_path.lower().endswith('.url')

def get_group_name(
  url_file_path: str,
):
  try:
    with open(url_file_path, 'r', encoding='utf-8') as f:
      for line in f:
        if line.strip().startswith('URL='):
          match = re.match(r'URL=(.+?)://', line)
          if match:
            protocol = match.group(1)
            if protocol in PROTOCOL_MAP:
              return PROTOCOL_MAP[protocol]
            parts = re.split(r'[-_]', protocol)
            return ' '.join(p.capitalize() for p in parts)
  except Exception as ex:
    logger.error(f'Failed to read {url_file_path}: {ex}')
  return None

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

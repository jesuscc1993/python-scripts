import os
import re
import sys
import winsound

from mtlogger import logger
from mtprompt import Prompt

from _common import process_parent_folder

PROTOCOL_MAP = {
  'com.epicgames.launcher': 'Epic Games'
}

def main():
  parent_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the files you want to group:')

  process_parent_folder(parent_dir, should_process_item, get_group_name)

def should_process_item(item_path):
  return os.path.isfile(item_path) and item_path.lower().endswith('.url')

def get_group_name(url_file):
  try:
    with open(url_file, 'r', encoding='utf-8') as f:
      for line in f:
        if line.strip().startswith('URL='):
          match = re.match(r'URL=(.+?)://', line)
          if match:
            protocol = match.group(1)
            if protocol in PROTOCOL_MAP:
              return PROTOCOL_MAP[protocol]
            parts = re.split(r'[-_]', protocol)
            return ' '.join(p.capitalize() for p in parts)
  except Exception as e:
    logger.error(f'Failed to read {url_file}: {e}')
  return None

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')

  winsound.MessageBeep()
  Prompt.enterToExit()

import os

from mtlogger import logger
from mtprompt import Prompt

from _common import delete_children_for_dirs

CHROME_PATH = r'%LOCALAPPDATA%\Google\Chrome\User Data\Default'
FIREFOX_PATH = r'%LOCALAPPDATA%\Mozilla\Firefox\Profiles\*'

DIR_PATTERNS = [
  os.path.join(CHROME_PATH, r'*cache*'),
  os.path.join(CHROME_PATH, r'Service Worker\CacheStorage'),

  os.path.join(FIREFOX_PATH, r'*cache*'),
]

def main():
  delete_children_for_dirs(DIR_PATTERNS)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

from mtfs import read_json_file, write_json_file
from mthltb import Hltb
from mtlogger import logger
from mtprompt import Prompt

from _constants import HLTB_DB_PATH

def main():
  db = read_json_file(HLTB_DB_PATH) or {}

  while True:
    folder_name = Prompt.str('Enter the game folder name, or press Enter to exit', optional=True)
    if not folder_name:
      return

    fallback_name = Prompt.str('Enter the fallback game name to search for')
    result = Hltb.search(fallback_name)

    if result is None:
      logger.warn(f'No HLTB result found for "{fallback_name}".')
      logger.hr()
      continue

    db[folder_name] = result
    write_json_file(HLTB_DB_PATH, db)
    logger.success(f'Saved HLTB result for "{folder_name}" using "{fallback_name}".')
    logger.hr()

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

import sys

from mtfs import read_json_file
from mtlogger import logger
from mtprompt import Prompt

from _common import scan_dir_names
from _common_hltb import generate_hltb_scan_for_game_names
from _constants import GENERIC_EXCLUSION_FILE, HLTB_DB_PATH, HLTB_EXCLUSION_FILE

OUTPUT_FILENAME = 'hltb_report.md'

def main():
  logger.log('Running HowLongToBeat scan...')

  game_dirs = sys.argv[1:] if len(sys.argv) > 1 else [Prompt.dir('Enter the path to the directory containing your games')]

  dir_names = scan_dir_names(game_dirs, [GENERIC_EXCLUSION_FILE, HLTB_EXCLUSION_FILE])
  db = read_json_file(HLTB_DB_PATH) or {}
  generate_hltb_scan_for_game_names(dir_names, db, OUTPUT_FILENAME)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

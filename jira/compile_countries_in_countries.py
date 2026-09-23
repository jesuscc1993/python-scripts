import re
import sys

from mtlogger import logger
from mtprompt import Prompt, to_list

from _common import find_in_issue_ids

CODE_PATTERN = re.compile(r'\b[A-Z]{2}\b')

def main():
  if len(sys.argv) > 1:
    issue_ids = to_list(sys.argv[1])
  else:
    issue_ids = Prompt.list('Enter issue IDs (comma-separated)')

  if not issue_ids:
    logger.error('No issue IDs provided.')
    return

  combined_countries = find_in_issue_ids(issue_ids, CODE_PATTERN)
  logger.log(f'\nComplete set of countries:\n  [{", ".join(sorted(combined_countries))}]\nFor issue IDs:\n  [{", ".join(issue_ids)}]')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

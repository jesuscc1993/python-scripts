import re
import sys

from mtlogger import logger
from mtprompt import Prompt, to_list

from _common import find_in_issue_ids

LOCALE_PATTERN = re.compile(r'\b[a-z]{2}(?:-[A-Za-z]+)?-[A-Z]{2}\b')

def main():
  if len(sys.argv) > 1:
    issue_ids = to_list(sys.argv[1])
  else:
    issue_ids = Prompt.list('Enter issue IDs (comma-separated)')

  if not issue_ids:
    logger.error('No issue IDs provided.')
    return

  combined_locales = find_in_issue_ids(issue_ids, LOCALE_PATTERN)
  logger.log(f'\nComplete set of locales:\n  [{", ".join(sorted(combined_locales))}]\nFor issue IDs:\n  [{", ".join(issue_ids)}]')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

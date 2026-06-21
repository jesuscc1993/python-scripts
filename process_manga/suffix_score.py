
import os
import re
import sys

from mal import MangaSearch
from mtlogger import logger
from mtprompt import Prompt

MAX_RESULTS = 5

def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your manga'
    )

  logger.log(f'Suffixing scores in "{parent_dir}"...')

  for entry in os.scandir(parent_dir):
    if entry.is_dir() and not re.fullmatch(r'[\(\[\{].*[\)\]\}]', entry.name):
      process_dir(entry.path)

  logger.success(f'Finished suffixing scores in "{parent_dir}".')

def process_dir(dir):
  dir_name = os.path.basename(dir)

  if re.search(r'\{\d{1,3}\}', dir_name):
    logger.trace(f'Skipping "{dir_name}". Already has a score suffix.')
    return

  name = re.sub(r'\s*\{\d{1,3}\}\s*$', '', dir_name).strip()

  try:
    results = MangaSearch(name).results
    if not results:
      logger.warn(f'Skipping "{dir_name}". No results found.')
      return

    results = [r for r in results if r.score][:MAX_RESULTS]

    if not results:
      logger.warn(f'Skipping "{dir_name}". No scored results.')
      return

    for result in results:
      result.score_int = round(float(result.score) * 10)

    exact_match = next((r for r in results if r.title.lower() == name.lower()), None)
    if exact_match:
      result = exact_match
    else:
      print(f'\n{name}')
      for i, result in enumerate(results):
        prefix = f'({i + 1})' if i == 0 else f' {i + 1} '
        print(f'{prefix} {result.title} — {result.score_int}')
      print(f' X  Skip')

      choice = input('> ').strip()
      if not choice:
        choice = 1
      elif choice.upper() == 'X':
        logger.trace(f'Skipped "{dir_name}".')
        return

      result = results[(int(choice) - 1) if choice else 0]

    new_name = f'{dir_name} {{{result.score_int}}}'
    new_path = os.path.join(os.path.dirname(dir), new_name)
    os.rename(dir, new_path)
    logger.success(f'Renamed "{dir_name}" -> "{new_name}".')
  except Exception as ex:
    logger.error(f'Error processing "{dir_name}": {ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit(timeout=True)

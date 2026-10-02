import os
import re
import requests
import sys

from typing import Union

from mal import Anime, AnimeSearch, AnimeSearchResult, Manga, MangaSearch, MangaSearchResult, config
from mtlogger import logger
from mtprompt import Prompt

ANIME_MEDIA_TYPE = 'anime'
MANGA_MEDIA_TYPE = 'manga'
MEDIA_TYPES = [ANIME_MEDIA_TYPE, MANGA_MEDIA_TYPE]

TYPE_BLACKLIST = {
  ANIME_MEDIA_TYPE: [],
  MANGA_MEDIA_TYPE: ['Light Novel', 'Novel'],
}
MAX_RESULTS = 9
NO_RESULTS_FOUND_ERROR = 'No results found'

ENTRY_URL_REGEX = re.compile(r'^https://myanimelist\.net/(anime|manga)/(\d+)/')

def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
    media_type = sys.argv[2]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your media'
    )
    media_type = Prompt.option(
      MEDIA_TYPES,
      f'Select the media type',
      default=ANIME_MEDIA_TYPE
    )

  if media_type not in MEDIA_TYPES:
    logger.error(f'Invalid media type: "{media_type}". Must be one of {', '.join(MEDIA_TYPES)}.')
    return

  logger.log(f'Suffixing scores in "{parent_dir}"...')
  logger.hr()

  for entry in os.scandir(parent_dir):
    if entry.is_dir() and not re.fullmatch(r'[\(\[\{].*[\)\]\}]', entry.name):
      process_dir(entry.path, media_type)
      logger.hr()

  logger.success(f'Finished suffixing scores in "{parent_dir}".')

def process_dir(
  dir_path: str,
  media_type: str,
):
  dir_name = os.path.basename(dir_path)

  if re.search(r'\{\d{1,3}\}', dir_name):
    logger.trace(f'Skipping "{dir_name}". Already has a score suffix.')
    return

  name = dir_name.strip()
  name = re.sub(r'\s*\(.*?\)\s*', '', name)
  name = re.sub(r'\s*\{\d{1,3}\}\s*$', '', name)
  suffix_dir_score(dir_path, name, media_type)

def find_exact_match(name: str, media_type: str):
  mal_type = 'anime' if media_type == ANIME_MEDIA_TYPE else 'manga'
  response = requests.get(f'{config.MAL_ENDPOINT}{mal_type}.php?q={name}', timeout=10)

  match = ENTRY_URL_REGEX.match(response.url)
  if not match:
    return None

  mal_id = int(match.group(2))
  return Anime(mal_id) if media_type == ANIME_MEDIA_TYPE else Manga(mal_id)

def suffix_dir_score(dir_path: str, name: str, media_type: str):
  dir_name = os.path.basename(dir_path)

  try:
    search_cls = AnimeSearch if media_type == ANIME_MEDIA_TYPE else MangaSearch
    try:
      results = [r for r in search_cls(name).results if r.type not in TYPE_BLACKLIST[media_type]][:MAX_RESULTS]
      if not results:
        # manually raise NO_RESULTS_FOUND_ERROR after filtering blacklist,
        # to route into the same handling as no results found by the library
        raise ValueError(NO_RESULTS_FOUND_ERROR)
    except ValueError as ex:
      if str(ex) == NO_RESULTS_FOUND_ERROR:
        # MAL redirects straight to the entry page on an exact title match,
        # which the library mistakes for a search page with no results
        exact_match = find_exact_match(name, media_type)
        if exact_match is None:
          logger.warn(f'  Skipping "{dir_name}". No results found for query "{name}".')
          return
        results = [exact_match]
      else:
        raise

    results = [r for r in results if r.score][:MAX_RESULTS]
    if not results:
      logger.warn(f'Skipping "{dir_name}". No scored results for query "{name}".')
      return

    for result in results:
      result.score_int = round(float(result.score) * 10)

    exact_match = next((r for r in results if r.title.lower() == name.lower()), None)
    if exact_match:
      result = exact_match
    elif len(results) == 1:
      result = results[0]
    else:
      logger.log(f'{name}:')
      for i, result in enumerate(results):
        prefix = f'({i + 1})' if i == 0 else f' {i + 1} '
        logger.log(f'{prefix} {format_result_title(result)} — {result.score_int}')
      logger.trace(f' X  Skip')

      choice = input('> ').strip()
      if not choice:
        choice = 1
      elif choice.upper() == 'X':
        logger.trace(f'Skipped "{dir_name}".')
        return
      elif not choice.isdigit():
        logger.log()
        suffix_dir_score(dir_path, choice, media_type)
        return

      result = results[(int(choice) - 1) if choice else 0]

    new_dir_name = f'{dir_name} {{{result.score_int}}}'
    new_dir_path = os.path.join(os.path.dirname(dir_path), new_dir_name)
    os.rename(dir_path, new_dir_path)
    logger.success(f'Renamed "{dir_name}" -> "{new_dir_name}".')
  except Exception as ex:
    logger.error(f'Error processing "{dir_name}": {ex}')

def format_result_title(result: Union[AnimeSearchResult, MangaSearchResult]):
  return f'{result.title} {logger.format_trace("(" + result.type + ")")}'

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

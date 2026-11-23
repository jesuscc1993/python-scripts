import os
import re
import requests
import sys

from mal import Manga, MangaSearch, MangaSearchResult, config
from mtattr import Attr
from mtlogger import logger
from mtprompt import Prompt
from xml.etree import ElementTree

MAX_RESULTS = 9
TYPE_BLACKLIST = ['Light Novel', 'Novel']

COMIC_INFO_FILENAME = 'ComicInfo.xml'
COVER_FILENAME = 'cover.jpg'
NO_META_FILES = ['.noxml', '.nomedia']
HIDDEN_FILES = NO_META_FILES + [COMIC_INFO_FILENAME]
ALL_FILES = HIDDEN_FILES + [COVER_FILENAME]

NO_RESULTS_FOUND_ERROR = 'No results found'

ENTRY_URL_REGEX = re.compile(r'^https://myanimelist\.net/manga/(\d+)/')


def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your manga'
    )

  logger.log(f'Generating metadata in "{parent_dir}"...')
  logger.hr()

  for entry in os.scandir(parent_dir):
    if entry.is_dir() and not re.fullmatch(r'[\(\[\{].*[\)\]\}]', entry.name):
      process_dir(entry.path)
      logger.hr()

  logger.success(f'Finished generating metadata in "{parent_dir}".')


def process_dir(
  dir_path: str,
):
  dir_name = os.path.basename(dir_path)

  files_missing = []
  for filename in ALL_FILES:
    file_path = os.path.join(dir_path, filename)

    if not os.path.exists(file_path):
      files_missing.append(filename)
    elif filename in HIDDEN_FILES and not Attr.is_hidden(file_path):
      Attr.hide(file_path)

  if not files_missing:
    logger.trace(f'  Skipping "{dir_name}". All metadata files already exist.')
    return

  sanitized_name = re.sub(r'\s*\{.*?\}\s*', '', dir_name).strip()
  fetch_manga_info(dir_path, sanitized_name)
  logger.log()
  generate_no_meta_files(dir_path)


def format_result_title(result: MangaSearchResult):
  return f'{result.title} {logger.format_trace("(" + result.type + ")")}'


def find_exact_match(name: str):
  response = requests.get(
    f'{config.MAL_ENDPOINT}manga.php?q={name}', timeout=10
  )

  match = ENTRY_URL_REGEX.match(response.url)
  if not match:
    return None

  return Manga(int(match.group(1)))


def write_comic_info(
  manga: Manga,
  file_path: str,
):
  root = ElementTree.Element('ComicInfo')

  add_xml_field(root, 'Title', manga.title)
  add_xml_field(
    root,
    'Summary',
    (
      re.sub(r'\s*\[Written by MAL Rewrite\]\s*$', '', manga.synopsis)
      if manga.synopsis
      else None
    ),
  )
  add_xml_field(root, 'Writer', ', '.join(manga.authors))
  add_xml_field(root, 'CommunityRating', format_score(manga.score))
  add_xml_field(root, 'Genre', ', '.join(manga.genres))

  tree = ElementTree.ElementTree(root)
  ElementTree.indent(tree, space='  ')
  tree.write(file_path, encoding='utf-8', xml_declaration=True)

  if os.path.basename(file_path) in HIDDEN_FILES:
    Attr.hide(file_path)

  logger.success(f'Generated "{format_path(file_path)}" file.')


def add_xml_field(
  root: ElementTree.Element,
  tag: str,
  value: str,
):
  if value:
    ElementTree.SubElement(root, tag).text = str(value)


def format_score(
  score: float,
):
  return score / 2 if score else None


def generate_no_meta_files(
  dir_path: str,
):
  for filename in NO_META_FILES:
    try:
      file_path = os.path.join(dir_path, filename)
      formatted_file_path = format_path(file_path)

      if os.path.exists(file_path):
        logger.trace(
          f'  Skipping "{formatted_file_path}". File already exists.'
        )
      else:
        open(file_path, 'w').close()
        if filename in HIDDEN_FILES:
          Attr.hide(file_path)
        logger.success(f'Created "{formatted_file_path}" file.')

    except Exception as ex:
      logger.error(f'Could not create "{filename}":\n{ex}')


def fetch_manga_info(dir_path: str, name: str):
  dir_name = os.path.basename(dir_path)
  comic_info_path = os.path.join(dir_path, COMIC_INFO_FILENAME)
  formatted_comic_info_path = format_path(comic_info_path)

  if not os.path.exists(comic_info_path):
    try:
      try:
        results = [
          r for r in MangaSearch(name).results if r.type not in TYPE_BLACKLIST
        ][:MAX_RESULTS]
        if not results:
          # manually raise NO_RESULTS_FOUND_ERROR after filtering blacklist,
          # to route into the same handling as no results found by the library
          raise ValueError(NO_RESULTS_FOUND_ERROR)
      except ValueError as ex:
        if str(ex) == NO_RESULTS_FOUND_ERROR:
          # MAL redirects straight to the entry page on an exact title match,
          # which the library mistakes for a search page with no results
          exact_match = find_exact_match(name)
          if exact_match is None:
            logger.warn(
              f'  Skipping "{dir_name}". No results found for query "{name}".'
            )
            return
          results = [exact_match]
        else:
          raise

      exact_match = next(
        (r for r in results if r.title.lower() == name.lower()), None
      )
      if exact_match:
        result = exact_match
      elif len(results) == 1:
        result = results[0]
      else:
        logger.log(f'{name}:')
        for i, result in enumerate(results):
          prefix = f'({i + 1})' if i == 0 else f' {i + 1} '
          logger.log(f'{prefix} {format_result_title(result)}')
        logger.trace(' X  Skip')

        choice = input('> ').strip()
        if not choice:
          choice = '1'
        elif choice.upper() == 'X':
          logger.trace(f'  Skipped "{formatted_comic_info_path}".')
          return
        elif not choice.isdigit():
          fetch_manga_info(dir_path, choice)
          return

        result = results[(int(choice) - 1) if choice else 0]

      manga = Manga(result.mal_id)
      cover_path = os.path.join(dir_path, COVER_FILENAME)

      write_comic_info(manga, comic_info_path)
      generate_cover_image(manga, cover_path)

    except Exception as ex:
      logger.error(f'Error processing "{dir_name}": {ex}')

  else:
    logger.trace(
      f'  Skipping "{formatted_comic_info_path}". File already exists.'
    )


def generate_cover_image(
  manga: Manga,
  cover_path: str,
):
  formatted_cover_path = format_path(cover_path)

  if os.path.exists(cover_path):
    logger.trace(f'  Skipping "{formatted_cover_path}". File already exists.')
    return

  if not manga.image_url:
    logger.warn(f'  Skipping "{formatted_cover_path}". No cover image found.')
    return

  try:
    response = requests.get(
      manga.image_url.replace('.jpg', 'l.jpg'), timeout=10
    )
    response.raise_for_status()

    with open(cover_path, 'wb') as file:
      file.write(response.content)

    logger.success(f'Generated "{formatted_cover_path}" file.')

  except Exception as ex:
    logger.error(f'Could not save "{formatted_cover_path}":\n{ex}')


def format_path(file_path: str):
  return os.path.join(
    os.path.basename(os.path.dirname(file_path)), os.path.basename(file_path)
  )


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

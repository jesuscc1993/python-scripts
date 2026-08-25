import os
import re
import requests
import sys

from mal import Manga, MangaSearch, MangaSearchResult
from mtattr import Attr
from mtlogger import logger
from mtprompt import Prompt
from xml.etree import ElementTree

MAX_RESULTS = 9
TYPE_BLACKLIST = ['Light Novel', 'Novel']

COMIC_INFO_FILENAME = 'ComicInfo.xml'
COVER_FILENAME = 'cover.jpg'
NO_META_FILES = ['.noxml', '.nomedia']
ALL_FILES = [COMIC_INFO_FILENAME, COVER_FILENAME] + NO_META_FILES

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

  files_missing = [f for f in ALL_FILES if not os.path.exists(os.path.join(dir_path, f))]
  if not files_missing:
    logger.trace(f'  Skipping "{dir_name}". All metadata files already exist.')
    return

  sanitized_name = re.sub(r'\s*\{\d{1,3}\}\s*$', '', dir_name).strip()
  generate_no_meta_files(dir_path)
  fetch_manga_info(dir_path, sanitized_name)

def format_result_title(result: MangaSearchResult):
  return f'{result.title} {logger.formatTrace("(" + result.type + ")")}'

def write_comic_info(
  dir_path: str,
  file_path: str,
  manga: Manga,
):
  root = ElementTree.Element('ComicInfo')

  add_xml_field(root, 'Title', manga.title)
  add_xml_field(root, 'Summary', manga.synopsis)
  add_xml_field(root, 'Writer', ', '.join(manga.authors))
  add_xml_field(root, 'CommunityRating', format_score(manga.score))
  add_xml_field(root, 'Genre', ', '.join(manga.genres))

  tree = ElementTree.ElementTree(root)
  ElementTree.indent(tree, space='  ')
  tree.write(file_path, encoding='utf-8', xml_declaration=True)

  rel_file_path = os.path.join(os.path.basename(dir_path), os.path.basename(file_path))
  logger.success(f'Generated "{rel_file_path}" file.')

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
      rel_file_path = os.path.join(os.path.basename(dir_path), filename)

      if os.path.exists(file_path):
        if Attr.is_hidden(file_path):
          logger.trace(f'  Skipping "{rel_file_path}". File already exists.')
        else:
          Attr.hide(file_path)
          logger.success(f'Hid existing "{rel_file_path}" file.')
      else:
        open(file_path, 'w').close()
        Attr.hide(file_path)
        logger.success(f'Created hidden "{rel_file_path}" file.')

    except Exception as ex:
      logger.error(f'Could not create "{filename}":\n{ex}')

def fetch_manga_info(dir_path: str, name: str):
  dir_name = os.path.basename(dir_path)
  comic_info_path = os.path.join(dir_path, COMIC_INFO_FILENAME)
  rel_comic_info_path = os.path.join(dir_name, COMIC_INFO_FILENAME)

  if not os.path.exists(comic_info_path):
    logger.log()

    try:
      results = [r for r in MangaSearch(name).results if r.type not in TYPE_BLACKLIST][:MAX_RESULTS]
      if not results:
        logger.warn(f'Skipping "{dir_name}". No results found.')
        return

      exact_match = next((r for r in results if r.title.lower() == name.lower()), None)
      if exact_match:
        result = exact_match
      else:
        logger.log(f'{name}:')
        for i, result in enumerate(results):
          prefix = f'({i + 1})' if i == 0 else f' {i + 1} '
          logger.log(f'{prefix} {format_result_title(result)}')
        logger.trace(f' X  Skip')

        choice = input('> ').strip()
        if not choice:
          choice = 1
        elif choice.upper() == 'X':
          logger.trace(f'  Skipped "{rel_comic_info_path}".')
          return
        elif not choice.isdigit():
          fetch_manga_info(dir_path, choice)
          return

        result = results[(int(choice) - 1) if choice else 0]

      manga = Manga(result.mal_id)

      write_comic_info(dir_path, comic_info_path, manga)
      generate_cover_image(dir_path, manga)

    except Exception as ex:
      logger.error(f'Error processing "{dir_name}": {ex}')

  else:
    logger.trace(f'  Skipping "{rel_comic_info_path}". File already exists.')

def generate_cover_image(
  dir_path: str,
  manga: Manga,
):
  cover_path = os.path.join(dir_path, COVER_FILENAME)
  rel_cover_path = os.path.join(os.path.basename(dir_path), COVER_FILENAME)

  if os.path.exists(cover_path):
    logger.trace(f'  Skipping "{rel_cover_path}". File already exists.')
    return

  if not manga.image_url:
    logger.warn(f'  Skipping "{rel_cover_path}". No cover image found.')
    return

  try:
    response = requests.get(manga.image_url.replace('.jpg', 'l.jpg'), timeout=10)
    response.raise_for_status()

    with open(cover_path, 'wb') as file:
      file.write(response.content)

    logger.success(f'Generated "{rel_cover_path}" file.')

  except Exception as ex:
    logger.error(f'Could not save "{rel_cover_path}":\n{ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit(timeout=True)

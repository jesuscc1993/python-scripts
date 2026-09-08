import os
import re
import unicodedata

from mtattr import Attr
from mtfs import read_json_file
from mtlogger import logger

from _constants import DIR_BLACKLIST, GENERIC_EXCLUSION_FILE

def validate_dir_paths(
  dir_paths: list[str],
):
  for dir_path in dir_paths:
    if not os.path.isdir(dir_path):
      raise ValueError(f'Path "{dir_path}" is not a directory.')

def read_steam_wishlist_game_names(
  wishlist_file: str,
):
  wishlist_content = read_json_file(wishlist_file)
  if wishlist_content is None:
    raise ValueError(f'Could not read wishlist file "{wishlist_file}".')

  return [
    app_name
    for app in wishlist_content
    if not app.get('store_item', {}).get('is_coming_soon')
    if (app_name := get_app_name_from_steam_wishlist_item(app))
  ]

def get_app_name_from_steam_wishlist_item(app: dict):
  store_item = (app or {}).get('store_item')
  if not store_item:
    return None

  app_name = store_item.get('name')
  if not app_name:
    return None

  return app_name

def scan_dir_names(
  dir_paths: list[str],
  exclusions: list[str] = [GENERIC_EXCLUSION_FILE],
):
  return [
    entry.name
    for dir_path in dir_paths
    for entry in os.scandir(dir_path)
    if entry.is_dir() and not should_skip_dir(entry.path, exclusions)
  ]

def should_skip_dir(
  dir_path: str,
  exclusions: list[str],
):
  if Attr.is_hidden(dir_path):
    logger.trace(f'  Skipping "{dir_path}". Directory is hidden.')
    return True

  if os.path.basename(dir_path) in DIR_BLACKLIST:
    logger.trace(f'  Skipping "{dir_path}". Directory is blacklisted.')
    return True

  if any(has_exclusion_file(dir_path, exclusion) for exclusion in exclusions):
    logger.trace(f'  Skipping "{dir_path}". Directory is excluded.')
    return True

  return False

def has_exclusion_file(
  path: str,
  exclusion: str,
):
  return os.path.exists(os.path.join(path, exclusion))

def seconds_to_hours(
  seconds: int,
):
  return round(seconds / 3600) if seconds is not None else None

def format_dimmed(
  msg: str,
):
  return f'<span class="dim">{msg}</span>'

def simplify_game_name(
  name: str,
):
  parsed_name = name
  parsed_name = re.sub(r'[™®]', '', parsed_name)
  parsed_name = re.sub(r'([:-]\s?)?(GOTY|Game of The Year|Director.s Cut)(\sEdition)?', '', parsed_name, flags = re.IGNORECASE)
  parsed_name = re.sub(r'([:-]\s?)?(Definitive|Deluxe|Gold|Premium|Ultimate)\sEdition', '', parsed_name, flags = re.IGNORECASE)
  parsed_name = re.sub(r'[:-]\s?(\w+)\sEdition', '', parsed_name, flags = re.IGNORECASE)
  return parsed_name.strip()

def normalize_dir_name(
  name: str,
):
  parsed_name = name.lower()
  parsed_name = re.sub(r'[\'’:꞉—-]', '', parsed_name)
  parsed_name = ''.join(char for char in unicodedata.normalize('NFKD', parsed_name) if not unicodedata.combining(char))
  return parsed_name

def flatten_game_name(
  name: str,
):
  parsed_name = name
  parsed_name = re.sub(r'\b(HD|Remake|Remaster(?:ed)?)\b', '', parsed_name, flags = re.IGNORECASE)
  parsed_name = re.sub(r'(\s+)', '', parsed_name)
  return parsed_name

def get_comparable_dir_name(
  name: str,
):
  parsed_name = name
  parsed_name = simplify_game_name(parsed_name)
  parsed_name = normalize_dir_name(parsed_name)
  parsed_name = flatten_game_name(parsed_name)
  return parsed_name

def matches_loosely(
  name_a: str,
  name_b: str,
):
  return get_comparable_dir_name(name_a) == get_comparable_dir_name(name_b)

import os
import re
import unicodedata

from mtattr import Attr
from mtlogger import logger

from _constants import DIR_BLACKLIST, GENERIC_EXCLUSION_FILE

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
  formatted_name = name
  formatted_name = re.sub(r'[™®]', '', formatted_name)
  formatted_name = re.sub(r'([:-]\s?)?(GOTY|Game of The Year|Director\'s Cut)(\sEdition)?', '', formatted_name, flags = re.IGNORECASE)
  formatted_name = re.sub(r'([:-]\s?)?(Definitive|Deluxe|Gold|Premium|Ultimate)\sEdition', '', formatted_name, flags = re.IGNORECASE)
  formatted_name = re.sub(r'[:-]\s?(\w+)\sEdition', '', formatted_name, flags = re.IGNORECASE)
  return formatted_name.strip()

def normalize_dir_name(
  name: str,
):
  name = name.lower()
  name = re.sub(r'[:꞉’\']', '', name)
  name = ''.join(char for char in unicodedata.normalize('NFKD', name) if not unicodedata.combining(char))
  return name

def get_comparable_dir_name(
  name: str,
):
  comparable_name = re.sub(r'(\s+|-)', '', name)
  comparable_name = simplify_game_name(comparable_name)
  comparable_name = normalize_dir_name(comparable_name)
  return comparable_name

def matches_loosely(
  a: str,
  b: str,
):
  return get_comparable_dir_name(a) == get_comparable_dir_name(b)

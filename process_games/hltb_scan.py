import json
import os
import re
import sys

from mtlogger import logger
from mthltb import Hltb, HltbResult
from mtprompt import Prompt
from tqdm import tqdm

from _common import scan_dir_names, seconds_to_hours
from _constants import EMPTY_CELL, STYLE

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '_data', 'hltb_database.json')

def main():
  logger.log('Running HowLongToBeat scan...')

  game_dirs = sys.argv[1:] if len(sys.argv) > 1 else [Prompt.dir('Enter the path to the directory containing your games')]

  db = get_db()
  dir_names = scan_dir_names(game_dirs)

  matched = []
  unmatched = []

  for dir_name in tqdm(dir_names, desc='Scanning games'):
    result = get_cached_result(dir_name, db)
    if result is None:
      unmatched.append(dir_name)
      continue

    matched.append((dir_name, result))

  matched.sort(key=lambda x: x[1]['comp_plus'] or 0, reverse=True)
  unmatched.sort()
  write_output(matched, unmatched)

def get_cached_result(
  dir_name: str,
  db: dict,
):
  if dir_name in db:
    return db[dir_name]

  result = Hltb.search(dir_name)
  db[dir_name] = result
  save_db(db)
  return result

def get_db():
  if not os.path.exists(DB_PATH):
    return {}

  with open(DB_PATH, 'r', encoding='utf-8') as f:
    return json.load(f)

def save_db(
  db: dict,
):
  os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

  with open(DB_PATH, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2)

def write_output(
  matched: list,
  unmatched: list,
):
  lines = [
    '<title>HowLongToBeat Scan Output</title>',
    f'<style>{STYLE}</style>',
    '',
    f'# HowLongToBeat Scan Output',
    '',
  ]

  if len(matched):
    lines += [
      f'### Games Found {format_dimmed(f"(cache: [{os.path.basename(DB_PATH)}]({os.path.abspath(DB_PATH).replace(chr(92), "/")}))")}',
      '',
      '| Game | Matched | Main Story | Main + Extra | Completionist |',
      '|---|---|--:|--:|--:|',
    ]
    for dir_name, result in matched:
      game_cell = format_game_column(dir_name)
      matched_cell = format_matched_column(dir_name, result)
      lines.append(f'| {game_cell} | {matched_cell} | {format_hours_column(result["comp_main"])} | {format_hours_column(result["comp_plus"])} | {format_hours_column(result["comp_100"])} |')

  if len(unmatched):
    lines += [
      '',
      '### Games Not Found',
      '',
    ]
    for dir_name in unmatched:
      lines.append(f'- {dir_name}')

  tmp_dir = os.path.expandvars('%TEMP%')
  output_path = os.path.join(tmp_dir, 'hltb_scan_output.md')
  with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

  logger.success(f'Saved output to {output_path}')
  os.startfile(output_path)

def format_game_column(
  dir_name: str,
):
  return dir_name

def format_matched_column(
  dir_name: str,
  result: HltbResult,
):
  game_name = result['game_name']
  formatted_game_name = format_game_name(game_name)
  game_name_content = f'[{formatted_game_name}]({result["url"]})'
  return game_name_content if matches_loosely(dir_name, game_name) else format_dimmed(game_name_content)

def format_hours_column(
  seconds: int,
):
  hours = seconds_to_hours(seconds)
  return f'{hours:g}h' if hours is not None else EMPTY_CELL

def format_game_name(
  name: str,
):
  formatted_name = name
  formatted_name = re.sub(r'[™®]\s?', '', formatted_name)
  formatted_name = re.sub(r'([:-]\s?)?(GOTY|Game of The Year|Director\'s Cut)(\sEdition)?', '', formatted_name, flags = re.IGNORECASE)
  formatted_name = re.sub(r'([:-]\s?)?(Definitive|Deluxe|Gold|Premium|Ultimate)\sEdition', '', formatted_name, flags = re.IGNORECASE)
  formatted_name = re.sub(r'[:-]\s?(\w+)\sEdition', '', formatted_name, flags = re.IGNORECASE)
  return formatted_name.strip()

def format_dimmed(
  msg: str,
):
  return f'<span class="dim">{msg}</span>'

def normalize_dir_name(
  name: str,
):
  name = name.lower()
  name = re.sub(r'[:꞉’\']', '', name)
  return name

def matches_loosely(
  a: str,
  b: str,
):
  return (
    re.sub(r'\s+', '', normalize_dir_name(a)) ==
    re.sub(r'\s+', '', normalize_dir_name(b))
  )

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

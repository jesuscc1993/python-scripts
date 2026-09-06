import os
import sys

from mtlogger import logger
from mthltb import Hltb, HltbResult
from mtfs import read_json_file, write_json_file, write_text_file
from mtprompt import Prompt
from tqdm import tqdm

from _common import scan_dir_names, seconds_to_hours, format_dimmed, simplify_game_name, matches_loosely
from _constants import EMPTY_CELL, GENERIC_EXCLUSION_FILE, HLTB_DB_PATH, OUTPUT_DIR_PATH, STYLE

HLTB_EXCLUSION_FILE = '.nohltbscan'
OUTPUT_FILENAME = 'hltb_scan_output.md'

def main():
  logger.log('Running HowLongToBeat scan...')

  game_dirs = sys.argv[1:] if len(sys.argv) > 1 else [Prompt.dir('Enter the path to the directory containing your games')]

  db = read_json_file(HLTB_DB_PATH) or {}
  dir_names = scan_dir_names(game_dirs, [GENERIC_EXCLUSION_FILE, HLTB_EXCLUSION_FILE])

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
  cached_result = db.get(dir_name)
  if is_result_complete(cached_result):
    return cached_result

  result = Hltb.search(dir_name)
  db[dir_name] = result
  write_json_file(HLTB_DB_PATH, db)
  return result

def is_result_complete(
  result: HltbResult | None,
):
  return result and all(result.get(key) for key in ('comp_main', 'comp_plus', 'comp_100'))

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
      f'### Games Found {format_dimmed(f"(cache: [{os.path.basename(HLTB_DB_PATH)}]({os.path.abspath(HLTB_DB_PATH).replace(chr(92), "/")}))")}',
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

  output_path = os.path.join(OUTPUT_DIR_PATH, OUTPUT_FILENAME)
  write_text_file(output_path, '\n'.join(lines))

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
  formatted_game_name = simplify_game_name(game_name)
  game_name_content = f'[{formatted_game_name}]({result["url"]})'
  return game_name_content if matches_loosely(dir_name, game_name) else format_dimmed(game_name_content)

def format_hours_column(
  seconds: int,
):
  hours = seconds_to_hours(seconds)
  return f'{hours:g}h' if hours else EMPTY_CELL

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

import argparse
import os

from mtfs import read_json_file, write_json_file, write_text_file
from mthltb import Hltb, HltbResult
from mtlogger import logger
from mtprompt import Prompt, to_list
from tqdm import tqdm

from _common import format_dimmed, matches_loosely, read_steam_wishlist_game_names, scan_dir_names, seconds_to_hours, simplify_game_name, validate_dir_paths
from _constants import EMPTY_CELL, GAME_DIRS_SCAN_TYPE, GENERIC_EXCLUSION_FILE, HLTB_DB_PATH, HLTB_EXCLUSION_FILE, HLTB_OUTPUT_DIRNAME, OUTPUT_DIR_PATH, STYLE, WISHLIST_FILE_SCAN_TYPE

RESCAN_UNTRACKED = True

INSTALLED_GAMES_REPORT_FILENAME = 'hltb_report_for_installed_games.md'
STEAM_WISHLIST_REPORT_FILENAME = 'hltb_report_for_steam_wishlist.md'

def main():
  logger.log('Running HowLongToBeat scan...')

  args = create_parser().parse_args()
  if args.game_dirs:
    game_names, output_filename = scan_game_dirs(to_list(args.game_dirs))
  elif args.wishlist_file:
    game_names, output_filename = scan_wishlist_file(args.wishlist_file)
  else:
    game_names, output_filename = prompt_for_scan_type()

  db = read_json_file(HLTB_DB_PATH) or {}
  generate_hltb_scan_for_game_names(game_names, db, output_filename)

def prompt_for_scan_type():
  scan_type = Prompt.str('Enter scan type (game_dirs | wishlist_file)')

  if scan_type == GAME_DIRS_SCAN_TYPE:
    return scan_game_dirs(Prompt.list('Enter the game directories (path1, path2, ...)'))

  if scan_type == WISHLIST_FILE_SCAN_TYPE:
    return scan_wishlist_file(Prompt.file('Enter the Steam wishlist JSON file'))

  raise ValueError(f'Unknown scan type "{scan_type}". Use game_dirs or wishlist_file.')

def create_parser():
  parser = argparse.ArgumentParser()
  source_group = parser.add_mutually_exclusive_group()
  source_group.add_argument(f'--{GAME_DIRS_SCAN_TYPE}')
  source_group.add_argument(f'--{WISHLIST_FILE_SCAN_TYPE}')
  return parser

def scan_game_dirs(game_dirs: list[str]):
  validate_dir_paths(game_dirs)
  return scan_dir_names(game_dirs, [GENERIC_EXCLUSION_FILE, HLTB_EXCLUSION_FILE]), INSTALLED_GAMES_REPORT_FILENAME

def scan_wishlist_file(wishlist_file: str):
  return read_steam_wishlist_game_names(wishlist_file), STEAM_WISHLIST_REPORT_FILENAME

def generate_hltb_scan_for_game_names(
  game_names: list,
  db: dict,
  output_filename: str,
):
  matched = []
  untracked = []
  unmatched = []

  for game_name in tqdm(game_names, desc='Scanning games'):
    result = get_cached_result(game_name, db)
    if result is None:
      unmatched.append(game_name)
      continue
    if not has_playtime(result):
      untracked.append(game_name)
      continue

    matched.append((game_name, result))

  matched.sort(
    key=lambda item: (
      item[1].get('comp_plus') or
      item[1].get('comp_100') or
      item[1].get('comp_main') or
      0
    ),
    reverse=True,
  )
  untracked.sort()
  unmatched.sort()
  write_output(matched, untracked, unmatched, output_filename)

def get_cached_result(
  game_name: str,
  db: dict,
):
  cached_result = db.get(game_name)
  if not RESCAN_UNTRACKED or is_result_complete(cached_result):
    return cached_result

  result = Hltb.search(game_name)
  db[game_name] = result
  write_json_file(HLTB_DB_PATH, db)
  return result

def is_result_complete(
  result: HltbResult | None,
):
  return result and all(result.get(key) for key in ('comp_main', 'comp_plus', 'comp_100'))

def has_playtime(
  result: HltbResult,
):
  return any(result.get(key) for key in ('comp_main', 'comp_plus', 'comp_100'))

def write_output(
  matched: list,
  untracked: list,
  unmatched: list,
  output_filename: str,
):
  lines = [
    '<title>HowLongToBeat Report</title>',
    f'<style>{STYLE}</style>',
    '',
    '# HowLongToBeat Report',
    '',
  ]

  if len(matched):
    lines += [
      f'### Games Found {format_dimmed(f"(cache: [{os.path.basename(HLTB_DB_PATH)}]({os.path.abspath(HLTB_DB_PATH).replace(chr(92), "/")}))")}',
      '',
      '| Game | Matched | Main Story | Main + Extra | Completionist |',
      '|---|---|--:|--:|--:|',
    ]
    for game_name, result in matched:
      game_cell = format_game_column(game_name)
      matched_cell = format_matched_column(game_name, result)
      lines.append(f'| {game_cell} | {matched_cell} | {format_hours_column(result["comp_main"])} | {format_hours_column(result["comp_plus"])} | {format_hours_column(result["comp_100"])} |')

  if len(untracked):
    lines += [
      '',
      '### Games Without Reported Length',
      '',
    ]
    for game_name in untracked:
      lines.append(f'- {game_name}')

  if len(unmatched):
    lines += [
      '',
      '### Games Not Found',
      '',
    ]
    for game_name in unmatched:
      lines.append(f'- {game_name}')

  output_path = os.path.join(OUTPUT_DIR_PATH, HLTB_OUTPUT_DIRNAME, output_filename)
  write_text_file(output_path, '\n'.join(lines))

  logger.success(f'Saved output to {output_path}')
  os.startfile(output_path)

def format_game_column(
  game_name: str,
):
  return game_name

def format_matched_column(
  game_name: str,
  result: HltbResult,
):
  matched_game_name = result['game_name']
  formatted_game_name = simplify_game_name(matched_game_name)
  game_name_content = f'[{formatted_game_name}]({result["url"]})'
  return game_name_content if matches_loosely(game_name, matched_game_name) else format_dimmed(game_name_content)

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
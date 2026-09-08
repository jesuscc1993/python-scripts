import argparse
import os
import re

from mtlogger import logger
from mtfs import read_json_file, write_text_file
from mtprompt import Prompt, to_list
from rapidfuzz import process
from tqdm import tqdm

from _common import scan_dir_names, format_dimmed, simplify_game_name, matches_loosely, normalize_dir_name, read_steam_wishlist_game_names, validate_dir_paths
from _constants import COMPACT_GUI_EXCLUSION_FILE, EMPTY_CELL, GAME_DIRS_SCAN_TYPE, GENERIC_EXCLUSION_FILE, OUTPUT_DIR_PATH, STYLE, WISHLIST_FILE_SCAN_TYPE
from _types_compact_gui import CompType, DbEntry

DATABASE_PATH = r"%LOCALAPPDATA%\IridiumIO\CompactGUI\databasev2.json"
OUTPUT_DIRNAME = 'compact_gui'
INSTALLED_GAMES_REPORT_FILENAME = 'compact_gui_report_for_installed_games.md'
STEAM_WISHLIST_REPORT_FILENAME = 'compact_gui_report_for_steam_wishlist.md'
MATCHING_ACCURACY = 75

def main():
  logger.log('Running CompactGUI scan...')

  args = create_parser().parse_args()
  if args.game_dirs:
    dir_names, output_filename = scan_game_dirs(to_list(args.game_dirs))
  elif args.wishlist_file:
    dir_names, output_filename = scan_wishlist_file(args.wishlist_file)
  else:
    dir_names, output_filename = prompt_for_scan_type()

  db = get_db()
  if db is None:
    logger.error("Database could not be loaded. Aborting.")
    return

  db_by_folder = build_db_by_folder(db)
  db_folder_names = list(db_by_folder.keys())

  matched = []
  unmatched = []

  for dir_name in tqdm(dir_names, desc = 'Scanning games'):
    db_entry, score = match_dir_name(dir_name, db_by_folder, db_folder_names)
    if db_entry is None:
      unmatched.append(dir_name)
      continue

    best_result = get_best_compression_result(db_entry.get('CompressionResults'))
    matched.append((dir_name, db_entry, score, best_result))

  matched.sort(key = lambda x: get_savings(x[3]), reverse = True)
  unmatched.sort()
  write_output(matched, unmatched, output_filename)

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
  return scan_dir_names(game_dirs, [GENERIC_EXCLUSION_FILE, COMPACT_GUI_EXCLUSION_FILE]), INSTALLED_GAMES_REPORT_FILENAME

def scan_wishlist_file(wishlist_file: str):
  return read_steam_wishlist_game_names(wishlist_file), STEAM_WISHLIST_REPORT_FILENAME

def build_db_by_folder(
  db: list[DbEntry],
):
  db_by_folder = {}
  for entry in db:
    db_by_folder[normalize_dir_name(entry['GameName'])] = entry
    db_by_folder[normalize_dir_name(entry['FolderName'])] = entry
  return db_by_folder

def match_dir_name(
  dir_name: str,
  db_by_folder: dict,
  db_folder_names: list,
):
  dir_name_lower = normalize_dir_name(dir_name)
  db_entry = (
    db_by_folder.get(dir_name_lower) or
    db_by_folder.get(dir_name_lower.replace(' -', '')) or
    db_by_folder.get(dir_name_lower.replace(' ', ''))
  )
  if db_entry is not None:
    return db_entry, 100

  pattern = re.compile(r'\b' + re.escape(dir_name_lower) + r'\b')
  substring_matches = [name for name in db_folder_names if pattern.search(name)]
  if substring_matches:
    best = min(substring_matches, key = len)
    score = round(len(dir_name) / len(best) * 100)
    if score < MATCHING_ACCURACY:
      return None, None
    return db_by_folder[best], score

  result = process.extractOne(dir_name_lower, db_folder_names, score_cutoff = MATCHING_ACCURACY)
  if result and result[0] not in dir_name_lower:
    return db_by_folder[result[0]], result[1]

  return None, None

def write_output(
  matched: list,
  unmatched: list,
  output_filename: str,
):
  lines = [
    '<title>CompactGUI Report</title>',
    f'<style>{STYLE}</style>',
    '',
    f'# CompactGUI Report',
    '',
  ]

  if len(matched):
    lines += [
      f'### Games Found {format_dimmed(f"(source: [{os.path.basename(DATABASE_PATH)}]({os.path.expandvars(DATABASE_PATH).replace(chr(92), "/")}))")}',
      '',
      f'| Game | Matched {format_dimmed(f"(accuracy%)")} | Type | Before | After | Savings |',
      '|---|---|:-:|--:|--:|:-:|',
    ]
    for dir_name, entry, score, best_result in matched:
      game_cell = format_game_column(dir_name)
      matched_cell = format_matched_column(dir_name, entry, score)
      before_cell = format_before_column(best_result)
      savings_cell = format_savings_column(best_result)
      lines.append(f'| {game_cell} | {matched_cell} | {format_comp_type_column(best_result)} | {before_cell} | {format_after_column(best_result)} | {savings_cell} |')

  if len(unmatched):
    lines += [
      '',
      '### Games Not Found',
      '',
    ]
    for dir_name in unmatched:
      lines.append(f'- {dir_name}')

  output_path = os.path.join(OUTPUT_DIR_PATH, OUTPUT_DIRNAME, output_filename)
  write_text_file(output_path, '\n'.join(lines))

  logger.success(f'Saved output to {output_path}')
  os.startfile(output_path)

def format_game_column(
  dir_name: str,
):
  return dir_name

def format_matched_column(
  dir_name: str,
  entry: DbEntry,
  score: int,
):
  steam_id = entry.get('SteamID')
  game_name = entry.get('GameName')
  folder_name = entry.get('FolderName')
  if score < 100:
    if (
      matches_loosely(dir_name, game_name) or
      matches_loosely(dir_name, folder_name)
    ):
      score = 100

  formatted_game_name = simplify_game_name(game_name)
  game_name_content = f'[{formatted_game_name}](https://store.steampowered.com/app/{steam_id})' if steam_id else formatted_game_name
  return game_name_content if score == 100 else format_dimmed(f'{game_name_content} ({score:.0f}%)')

def format_comp_type_column(
  result: dict,
):
  if result is None:
    return EMPTY_CELL
  return format_comp_name(CompType(result['CompType']))

def format_before_column(
  result: dict,
):
  return format_size(result['BeforeBytes']) if result else EMPTY_CELL

def format_after_column(
  result: dict,
):
  return format_size(result['AfterBytes']) if result else EMPTY_CELL

def format_savings_column(
  result: dict,
):
  if result is None:
    return EMPTY_CELL
  savings = result['BeforeBytes'] - result['AfterBytes']
  pct = (savings / result['BeforeBytes']) * 100
  return format_flex([format_dimmed(f'↓{round(pct)}%'), format_size(savings)])

def get_best_compression_result(
  results: list,
):
  if not results:
    return None
  return (
    next((r for r in results if r['CompType'] == CompType.LZX), None) or
    next((r for r in results if r['CompType'] == CompType.XPRESS16K), None) or
    next((r for r in results if r['CompType'] == CompType.XPRESS8K), None) or
    next((r for r in results if r['CompType'] == CompType.XPRESS4K), None)
  )

def get_savings(
  result: dict,
):
  return result['BeforeBytes'] - result['AfterBytes'] if result else 0

def format_comp_name(
  comp_type: CompType,
):
  return comp_type.name.replace('XPRESS', 'X')

def format_size(
  b: int,
):
  gigabytes = b / 1024 ** 3
  return f'{round(gigabytes, 1) or 0.1:g} GB'

def format_flex(
  items: list[str],
):
  return f'<span class="justify-between">{"".join(items)}</span>'

def get_db():
  db_path = os.path.expandvars(DATABASE_PATH)
  db = read_json_file(db_path)
  if db is None:
    logger.error(f"Database file not found at {db_path}")

  return db

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout = True)

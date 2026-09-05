import json
import os
import re
import sys

from mtattr import Attr
from mtlogger import logger
from mtprompt import Prompt
from rapidfuzz import process

from _compact_gui_types import CompType, DbEntry

DATABASE_PATH = r"%LOCALAPPDATA%\IridiumIO\CompactGUI\databasev2.json"
EMPTY_CELL = 'N/A'
EXCLUSION_FILE = '.noscan'
MATCHING_ACCURACY = 75

def main():
  games_dirs = sys.argv[1:] if len(sys.argv) > 1 else [Prompt.dir('Enter the path to the directory containing your games')]

  db = get_db()
  if db is None:
    logger.error("Database could not be loaded. Aborting.")
    return

  all_matched = []
  all_unmatched = []

  for games_dir in games_dirs:
    matched, unmatched = process_dir(games_dir, db)
    all_matched.extend(matched)
    all_unmatched.extend(unmatched)

  all_matched.sort(key=lambda x: get_savings(x[3]), reverse=True)
  all_unmatched.sort()
  write_output(all_matched, all_unmatched)

def process_dir(
  dir_path: str,
  db: list[DbEntry],
):
  dir_names = [
    entry.name
    for entry in os.scandir(dir_path)
    if entry.is_dir() and not should_skip_dir(entry.path)
  ]

  db_by_folder = {}
  for entry in db:
    db_by_folder[normalize_dir_name(entry['GameName'])] = entry
    db_by_folder[normalize_dir_name(entry['FolderName'])] = entry
  db_folder_names = list(db_by_folder.keys())

  matched = []
  unmatched = []

  for dir_name in dir_names:
    dir_name_lower = normalize_dir_name(dir_name)
    db_entry = (
      db_by_folder.get(dir_name_lower) or
      db_by_folder.get(dir_name_lower.replace(' -', '')) or
      db_by_folder.get(dir_name_lower.replace(' ', ''))
    )
    score = 100
    if db_entry is None:
      pattern = re.compile(r'\b' + re.escape(dir_name_lower) + r'\b')
      substring_matches = [name for name in db_folder_names if pattern.search(name)]
      if substring_matches:
        best = min(substring_matches, key=len)
        score = round(len(dir_name) / len(best) * 100)
        if score < MATCHING_ACCURACY:
          unmatched.append(dir_name)
          continue
        db_entry = db_by_folder[best]
      else:
        result = process.extractOne(dir_name_lower, db_folder_names, score_cutoff=MATCHING_ACCURACY)
        if result and result[0] not in dir_name_lower:
          db_entry = db_by_folder[result[0]]
          score = result[1]
        else:
          unmatched.append(dir_name)
          continue
    matched.append((dir_name, db_entry, score))

  matched = [
    (dir_name, entry, score, get_best_compression_result(entry.get('CompressionResults')))
    for dir_name, entry, score in matched
  ]

  return matched, unmatched

def write_output(
  matched: list,
  unmatched: list,
):
  lines = [
    '<title>CompactGUI Scan Output</title>',
    '<style>th { text-align: center !important; } .dim { filter: brightness(0.5); } .justify-between { display:flex; justify-content:space-between; gap: 0.25em; }</style>',
    '',
    f'# CompactGUI Scan Output',
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

  tmp_dir = os.path.expandvars('%TEMP%')
  output_path = os.path.join(tmp_dir, 'compact_gui_scan_output.md')
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

  game_name_content = f'[{game_name}](https://store.steampowered.com/app/{steam_id})' if steam_id else game_name
  return game_name_content if score == 100 else format_dimmed(f'{game_name_content} ({score:.0f}%)')

def format_comp_type_column(
  result: dict,
):
  if result is None:
    return format_dimmed(EMPTY_CELL)
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

def format_dimmed(
  msg: str,
):
  return f'<span class="dim">{msg}</span>'

def should_skip_dir(
  dir_path: str,
):
  should_skip = Attr.is_hidden(dir_path) or has_exclusion_file(dir_path)
  if should_skip:
    logger.trace(f'  Skipping "{dir_path}". Directory is hidden or contains a {EXCLUSION_FILE} file.')
  return should_skip

def has_exclusion_file(
  path: str,
):
  return os.path.exists(os.path.join(path, EXCLUSION_FILE))

def normalize_dir_name(
  name: str,
  remove_spaces = False
):
  name = name.lower()
  name = re.sub(r'[:꞉’\']', '', name)
  if remove_spaces:
    name = re.sub(r'\s+', '', name)
  return name

def matches_loosely(
  a: str,
  b: str,
):
  return (
    normalize_dir_name(a, remove_spaces=True) ==
    normalize_dir_name(b, remove_spaces=True)
  )

def get_db():
  db_path = os.path.expandvars(DATABASE_PATH)
  if not os.path.exists(db_path):
    logger.error(f"Database file not found at {db_path}")
    return None

  with open(db_path, 'r', encoding='utf-8') as f:
    return json.load(f)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout = True)

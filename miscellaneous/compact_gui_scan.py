import json
import os
import re
import stat
import sys

from mtlogger import logger
from mtprompt import Prompt
from rapidfuzz import process

from _compact_gui_types import CompType, DbEntry

DATABASE_PATH = r"%LOCALAPPDATA%\IridiumIO\CompactGUI\databasev2.json"
EMPTY_CELL = 'N/A'
MATCHING_ACCURACY = 80

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

  all_matched.sort(key=lambda x: x[3], reverse=True)
  all_unmatched.sort()
  write_output(all_matched, all_unmatched)

def process_dir(
  dir_path: str,
  db: list[DbEntry],
):
  dir_names = [
    entry.name
    for entry in os.scandir(dir_path)
    if entry.is_dir() and not is_hidden(entry.path)
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
        db_entry = db_by_folder[best]
        score = round(len(dir_name) / len(best) * 100)
      else:
        result = process.extractOne(dir_name_lower, db_folder_names, score_cutoff=MATCHING_ACCURACY)
        if result and result[0] not in dir_name_lower:
          db_entry = db_by_folder[result[0]]
          score = result[1]
        else:
          unmatched.append(dir_name)
          continue
    matched.append((dir_name, db_entry, score))

  matched = [(dir_name, entry, score, get_max_space_saved(entry)) for dir_name, entry, score in matched]

  return matched, unmatched

def write_output(
  matched: list,
  unmatched: list,
):
  lines = [
    '<title>CompactGUI Scan Output</title>',
    '<style>.dim { opacity: 0.5; } .justify-between { display:flex; justify-content:space-between; gap: 0.25em; }</style>',
    '',
    f'# CompactGUI Scan Output',
    '',
  ]

  if len(matched):
    lines += [
      '### Games Found',
      '',
      f'| Game | Matched {format_dimmed(f"(accuracy%)")} | Original | XPRESS 4K | XPRESS 8K | XPRESS 16K | LZX | Savings |',
      '|---|---|--:|---|---|---|---|--:|',
    ]
    for dir_name, entry, score, max_savings in matched:
      r = entry['CompressionResults']
      game_cell = dir_name
      steam_id = entry.get('SteamID')
      game_name = f'[{entry["GameName"]}](https://store.steampowered.com/app/{steam_id})' if steam_id else entry['GameName']
      matched_cell = format_dimmed(f'{game_name} ({score:.0f}%)') if score == 100 else f'{game_name} {format_dimmed(f"({score:.0f}%)")}'
      original_cell = format_size_column(r[0]['BeforeBytes']) if r else EMPTY_CELL
      max_savings_cell = format_size(max_savings / 1024 ** 3) if r else EMPTY_CELL
      lines.append(f'| {game_cell} | {matched_cell} | {original_cell} | {format_compression_column(r, CompType.XPRESS4K)} | {format_compression_column(r, CompType.XPRESS8K)} | {format_compression_column(r, CompType.XPRESS16K)} | {format_compression_column(r, CompType.LZX)} | {max_savings_cell} |')

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

def get_max_space_saved(
  entry: DbEntry,
):
  results = entry['CompressionResults']
  if not results:
    return 0
  return max(r['BeforeBytes'] - r['AfterBytes'] for r in results)

def format_size_column(
  b: int,
):
  return format_size(b / 1024 ** 3)

def format_compression_column(
  results: list,
  comp_type: CompType,
):
  r = next((r for r in results if r['CompType'] == comp_type), None)
  if r is None:
    return format_flex([format_dimmed(EMPTY_CELL), ''])
  gb = r['AfterBytes'] / 1024 ** 3
  pct = (1 - r['AfterBytes'] / r['BeforeBytes']) * 100
  return format_flex([format_size(gb), format_dimmed(f'↓{round(pct)}%')])

def format_size(
  gigabytes: float,
):
  return f'{round(gigabytes, 1) or 0.1:g} GB'

def format_flex(
  items: list[str],
):
  return f'<div class="justify-between">{"".join(items)}</div>'

def format_dimmed(
  msg: str,
):
  return f'<span class="dim">{msg}</span>'

def is_hidden(
  path: str,
):
  return os.lstat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN

def normalize_dir_name(
  name: str,
):
  return re.sub(r'[:꞉’\']', '', name.lower())

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
    logger.unhandledError(ex)

  Prompt.enter_to_exit(timeout = True)

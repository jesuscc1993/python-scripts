import json
import os
import stat
import sys

from mtlogger import logger
from mtprompt import Prompt

from rapidfuzz import process

from _compact_gui_types import CompType, DbEntry

DATABASE_PATH = r"%LOCALAPPDATA%\IridiumIO\CompactGUI\databasev2.json"
EMPTY_CELL = '<span style="opacity:0.33;">N/A</span>'
MATCHING_ACCURACY = 75

def main():
  games_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing your games')

  db = get_db()
  if db is None:
    logger.error("Database could not be loaded. Aborting.")
    return

  process_dir(games_dir, db)

def process_dir(dir_path: str, db: list[DbEntry]):
  dir_names = [
    entry.name
    for entry in os.scandir(dir_path)
    if entry.is_dir() and not is_hidden(entry.path)
  ]

  db_by_folder = {entry['FolderName']: entry for entry in db}
  db_folder_names = list(db_by_folder.keys())

  matched = []
  unmatched = []

  for dir_name in dir_names:
    db_entry = db_by_folder.get(dir_name)
    score = 100
    if db_entry is None:
      result = process.extractOne(dir_name, db_folder_names, score_cutoff=MATCHING_ACCURACY)
      if result:
        db_entry = db_by_folder[result[0]]
        score = result[1]
      else:
        unmatched.append(dir_name)
        continue
    matched.append((dir_name, db_entry, score))

  matched.sort(key=lambda x: get_best_savings(x[1]), reverse=True)

  lines = [
    '# CompactGUI Scan Output',
    '',
  ]

  if len(matched):
    lines += [
      '### Games Found',
      '',
      '| Game | Matched | Uncompressed | XPRESS4K | XPRESS8K | XPRESS16K | LZX |',
      '|------|---------|--------------|----------|----------|-----------|-----|',
    ]
    for dir_name, entry, score in matched:
      r = entry['CompressionResults']
      uncompressed = format_size_column(r[0]['BeforeBytes']) if r else EMPTY_CELL
      matched_name = f'{entry["FolderName"]} ({score:.0f}%)' if entry['FolderName'] != dir_name else ''
      lines.append(f'| {dir_name} | {matched_name} | {uncompressed} | {format_compression_column(r, CompType.XPRESS4K)} | {format_compression_column(r, CompType.XPRESS8K)} | {format_compression_column(r, CompType.XPRESS16K)} | {format_compression_column(r, CompType.LZX)} |')

  if len(unmatched):
    lines += [
      '',
      '### Games Not Found',
      '',
      '| Game |',
      '|------|',
    ]
    for dir_name in unmatched:
      lines.append(f'| {dir_name} |')

  output_path = os.path.join(dir_path, 'compact_gui_scan_output.md')
  with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

  logger.success(f'Saved output to {output_path}')
  os.startfile(output_path)

def get_best_savings(entry: DbEntry):
  results = entry['CompressionResults']
  if not results:
    return 0
  return max(1 - r['AfterBytes'] / r['BeforeBytes'] for r in results)

def format_size_column(b: int):
  return f'{b / 1024 ** 3:.2f}GB'

def format_compression_column(results: list, comp_type: CompType):
  r = next((r for r in results if r['CompType'] == comp_type), None)
  if r is None:
    return EMPTY_CELL
  gb = r['AfterBytes'] / 1024 ** 3
  pct = (1 - r['AfterBytes'] / r['BeforeBytes']) * 100
  return f'{gb:.2f}GB ({pct:.1f}%)'

def is_hidden(path: str):
  return os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN

def get_db() -> list[DbEntry] | None:
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

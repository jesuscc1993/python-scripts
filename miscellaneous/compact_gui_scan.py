import json
import os
import stat
import sys

from mtlogger import logger
from mtprompt import Prompt

from rapidfuzz import process

from _compact_gui_types import CompType, DbEntry

DATABASE_PATH = r"%LOCALAPPDATA%\IridiumIO\CompactGUI\databasev2.json"

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
    if db_entry is None:
      result = process.extractOne(dir_name, db_folder_names, score_cutoff=70)
      if result:
        db_entry = db_by_folder[result[0]]
      else:
        unmatched.append(dir_name)
        continue
    matched.append((dir_name, db_entry))

  def best_savings(entry: DbEntry) -> float:
    results = entry['CompressionResults']
    if not results:
      return 0
    return max(1 - r['AfterBytes'] / r['BeforeBytes'] for r in results)

  matched.sort(key=lambda x: best_savings(x[1]), reverse=True)

  def fmt_size(b: int) -> str:
    return f'{b / 1024 ** 3:.2f}GB'

  def fmt_col(results: list, comp_type: CompType) -> str:
    r = next((r for r in results if r['CompType'] == comp_type), None)
    if r is None:
      return 'N/A'
    gb = r['AfterBytes'] / 1024 ** 3
    pct = (1 - r['AfterBytes'] / r['BeforeBytes']) * 100
    return f'{gb:.2f}GB ({pct:.1f}%)'

  lines = [
    '# CompactGUI Scan Output',
    '',
  ]

  if len(matched):
    lines += [
      '### Games Found',
      '',
      '| Game | Uncompressed | XPRESS4K | XPRESS8K | XPRESS16K | LZX |',
      '|------|--------------|----------|----------|-----------|-----|',
    ]
    for dir_name, entry in matched:
      r = entry['CompressionResults']
      uncompressed = fmt_size(r[0]['BeforeBytes']) if r else 'N/A'
      lines.append(f'| {dir_name} | {uncompressed} | {fmt_col(r, CompType.XPRESS4K)} | {fmt_col(r, CompType.XPRESS8K)} | {fmt_col(r, CompType.XPRESS16K)} | {fmt_col(r, CompType.LZX)} |')

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

  Prompt.enter_to_exit()

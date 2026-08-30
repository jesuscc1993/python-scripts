import os
import re
import sys

from difflib import SequenceMatcher
from mtlogger import logger
from mtprompt import Prompt

HEADER_PATTERN = re.compile(r'^Publication Order of', re.IGNORECASE)
YEAR_PATTERN = re.compile(r'\((\d{4})\)')
FUZZY_MATCH_THRESHOLD = 0.8

# Order file line format:
#  {NAME} (YEAR)... or {NAME} (YEAR)
#
# examples:
#  Tales (1845)
#  Tales (1845), Wiley & Putnam

def main():
  if len(sys.argv) > 2:
    parent_dir = sys.argv[1]
    order_file = sys.argv[2]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing the subfolders you want to order'
    )
    order_file = Prompt.file(
      'Enter the path to the order text file'
    )

  process_parent_folder(parent_dir, order_file)

def process_parent_folder(
  parent_dir: str,
  order_file: str,
):
  logger.log(f'Prefixing order in "{parent_dir}"...')

  entries = parse_order_entries(order_file)

  sub_dirs = [
    dir_name
    for dir_name in os.listdir(parent_dir)
    if os.path.isdir(os.path.join(parent_dir, dir_name))
  ]

  if not sub_dirs:
    order_subfolder_files(parent_dir, entries)
  else:
    for dir_name in sub_dirs:
      order_subfolder_files(os.path.join(parent_dir, dir_name), entries)

  logger.success(f'Finished prefixing order in "{parent_dir}".')

def order_subfolder_files(
  dir_path: str,
  entries: list,
):
  matches = []
  for file_name in os.listdir(dir_path):
    file_path = os.path.join(dir_path, file_name)
    if not os.path.isfile(file_path):
      continue

    title = extract_title(file_name)
    match = find_year(title, entries)
    if match is None:
      logger.warn(f'Skipping "{file_name}". No match found in the order file.')
      continue

    year, matched_title, is_exact = match
    if not is_exact and not Prompt.bool(f'Match "{title}" to "{matched_title}" ({year})?', default = True):
      logger.warn(f'Skipping "{file_name}". Match not confirmed.')
      continue

    matches.append((year, title, file_name))

  matches.sort(key = lambda match: (match[0], match[1]))
  num_digits = max(2, len(str(len(matches))))

  for index, (_, _, file_name) in enumerate(matches, start = 1):
    order_str = str(index).zfill(num_digits)
    new_file_name = insert_order_tag(file_name, order_str)
    if new_file_name != file_name:
      os.rename(os.path.join(dir_path, file_name), os.path.join(dir_path, new_file_name))
      logger.debug(f'Renamed "{file_name}" to "{new_file_name}".')

def extract_title(
  file_name: str,
):
  name = os.path.splitext(file_name)[0]
  name = re.sub(r'^(?:\[.*?\]\s*)+', '', name)
  name = re.sub(r'^-\s*', '', name)
  return name.strip()

def normalize(
  text: str,
):
  return re.sub(r'[^a-z0-9]', '', text.lower())

def find_year(
  title: str,
  entries: list,
):
  target = normalize(title)
  if not target:
    return None

  for variants, year in entries:
    for variant in variants:
      if normalize(variant) == target:
        return year, variant, True

  for variants, year in entries:
    for variant in variants:
      normalized_variant = normalize(variant)
      if normalized_variant and (normalized_variant in target or target in normalized_variant):
        return year, variant, False

  best_year, best_variant, best_ratio = None, None, 0
  for variants, year in entries:
    for variant in variants:
      ratio = SequenceMatcher(None, normalize(variant), target).ratio()
      if ratio > best_ratio:
        best_ratio, best_year, best_variant = ratio, year, variant

  return (best_year, best_variant, False) if best_ratio >= FUZZY_MATCH_THRESHOLD else None

def insert_order_tag(
  file_name: str,
  order_str: str,
):
  name, ext = os.path.splitext(file_name)
  name = re.sub(r'\s*\[\d+\]', '', name)

  brackets = list(re.finditer(r'\[.*?\]', name))
  if not brackets:
    return f'[{order_str}] {name}{ext}'

  insert_pos = brackets[-1].end()
  return f'{name[:insert_pos]} [{order_str}]{name[insert_pos:]}{ext}'

def parse_order_entries(
  order_file_path: str,
):
  entries = []
  pending_title = None

  with open(order_file_path, 'r', encoding = 'utf-8') as file:
    lines = [line.strip() for line in file if line.strip()]

  for line in lines:
    if HEADER_PATTERN.match(line) or line.startswith('-'):
      continue

    year_match = YEAR_PATTERN.search(line)
    if not year_match:
      pending_title = line
      continue

    title_part = line[:year_match.start()].split('\t')[0].strip()
    title = title_part if title_part else pending_title
    pending_title = None

    if title:
      variants = [variant.strip() for variant in title.split('/')]
      entries.append((variants, int(year_match.group(1))))

  return entries

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

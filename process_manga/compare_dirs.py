import json
import os
import re
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import ITEM_EXTENSIONS, get_volume_and_chapter

def main():
  if len(sys.argv) > 2:
    folder_a = sys.argv[1]
    folder_b = sys.argv[2]
  else:
    folder_a = Prompt.dir('Enter the path to the first folder you want to compare')
    folder_b = Prompt.dir('Enter the path to the second folder you want to compare')

  subfolders_a = get_subfolders(folder_a)
  subfolders_b = get_subfolders(folder_b)

  missing_in_a = []
  missing_in_b = []
  mismatches = []

  for item_name in sorted(set(subfolders_a.keys()) | set(subfolders_b.keys())):
    nameA = subfolders_a.get(item_name)
    nameB = subfolders_b.get(item_name)

    path_a = os.path.join(folder_a, nameA) if nameA else None
    path_b = os.path.join(folder_b, nameB) if nameB else None

    if path_a and path_b:
      range_a = get_subfolder_ranges(path_a)
      range_b = get_subfolder_ranges(path_b)

      if range_a and range_b:
        if range_a == range_b:
          logger.success(f'"{item_name}" has the same volumes and chapters in both folders.')
        else:
          mismatches.append(item_name)
          logger.log(f'  "{item_name}" has different volumes or chapters in the folders.')
          logger.failure(f'{logger.formatTrace(f"\"{folder_a}\"")} {print_range(range_a)} | {print_range(range_b)} {logger.formatTrace(f"\"{folder_b}\"")}')
      else:
        logger.trace(f'Failed to determine ranges for "{item_name}".')
    elif path_a:
      missing_in_b.append(item_name)
      logger.warn(f'  "{folder_a}" only: "{item_name}".')
    elif path_b:
      missing_in_a.append(item_name)
      logger.warn(f'  "{folder_b}" only: "{item_name}".')

  logger.hr()

  if missing_in_a:
    logger.warn(f'Missing in "{folder_a}" ({len(missing_in_a)}): {stringify(missing_in_a)}\n')

  if missing_in_b:
    logger.warn(f'Missing in "{folder_b}" ({len(missing_in_b)}): {stringify(missing_in_b)}\n')

  if mismatches:
    logger.failure(f'Mismatching ranges ({len(mismatches)}): {stringify(mismatches)}\n')

def stringify(obj):
  return json.dumps(obj, indent = 2)

def get_subfolders(parent_dir):
  results = {}
  for root, dirs, _ in os.walk(parent_dir):
    if root == parent_dir:
      continue
    dirs[:] = [d for d in dirs if not re.fullmatch(r'[\(\[\{].*[\)\]\}]', d)]
    if not dirs:
      rel = os.path.relpath(root, parent_dir)
      results[normalize_name(os.path.basename(rel))] = rel
  return results

def normalize_name(name):
  return re.sub(r'\s*(\{.*?\}|\(.*?\))\s*', '', name).strip()

def get_subfolder_ranges(folder):
  items = sorted([
    item
    for item in os.listdir(folder)
    if os.path.isdir(os.path.join(folder, item))
    or os.path.splitext(item)[1].lower().endswith(tuple(ITEM_EXTENSIONS))
  ])

  if len(items):
    firstItem = items[0]
    lastItem = items[-1]

    firstVolume, firstChapter = get_volume_and_chapter(firstItem)
    lastVolume, lastChapter = get_volume_and_chapter(lastItem)

    firstMissing = firstVolume is None and firstChapter is None
    lastMissing = lastVolume is None and lastChapter is None

    if firstMissing or lastMissing:
      if firstMissing:
        logger.trace(f'Could not determine volume or chapter for "{firstItem}".')
      if lastMissing:
        logger.trace(f'Could not determine volume or chapter for "{lastItem}".')
      return None

    volumeRange = (firstVolume, lastVolume) if firstVolume is not None and lastVolume is not None else None
    chapterRange = (firstChapter, lastChapter) if firstChapter is not None and lastChapter is not None else None
    return volumeRange, chapterRange
  else:
    return None

def print_range(range):
  if range:
    vol_range = range[0]
    ch_range = range[1]

    msg = ''
    if vol_range:
      msg += f'Vol.{vol_range[0]}..{vol_range[1]}'
    if vol_range and ch_range:
      msg += ' / '
    if ch_range:
      msg += f'Ch.{ch_range[0]}..{ch_range[1]}'
    return msg
  else:
    raise ValueError('Range is invalid')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

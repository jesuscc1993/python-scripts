import os
import re
import winsound

from mtlogger import logger
from mtprompt import Prompt

from _common import ITEM_EXTENSIONS, get_volume_and_chapter

def main():
  folderA = Prompt.dir('Enter the path to the first folder you want to compare')
  folderB = Prompt.dir('Enter the path to the second folder you want to compare')

  subfoldersA = get_subfolders(folderA)
  subfoldersB = get_subfolders(folderB)

  for item_name in sorted(set(subfoldersA.keys()) | set(subfoldersB.keys())):
    nameA = subfoldersA.get(item_name)
    nameB = subfoldersB.get(item_name)

    pathA = os.path.join(folderA, nameA) if nameA else None
    pathB = os.path.join(folderB, nameB) if nameB else None

    if pathA and pathB:
      rangeA = get_subfolder_ranges(pathA)
      rangeB = get_subfolder_ranges(pathB)

      if rangeA and rangeB:
        if rangeA == rangeB:
          logger.log(f'"{item_name}" has the same volumes and chapters in both folders.')
          logger.success(f'{print_range(rangeA)}')
        else:
          logger.log(f'"{item_name}" has different volumes or chapters in the folders.')
          logger.failure(f'[{folderA}]: {print_range(rangeA)}')
          logger.failure(f'[{folderB}]: {print_range(rangeB)}')
      else:
        logger.dim(f'Failed to determine ranges for "{item_name}".')
    elif pathA:
      logger.warn(f'"{item_name}" exists in "{folderA}" but not in "{folderB}".')
    elif pathB:
      logger.warn(f'"{item_name}" exists in "{folderB}" but not in "{folderA}".')

def get_subfolders(dir):
  subfolders = [f for f in os.listdir(dir) if os.path.isdir(os.path.join(dir, f))]
  return {normalize_name(f): f for f in subfolders}

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

    firstFound = firstVolume is not None or firstChapter is not None
    lastFound = lastVolume is not None or lastChapter is not None

    if not firstFound or not lastFound:
      if not firstFound:
        logger.dim(f'Could not determine volume or chapter for "{firstItem}".')
      if not lastFound:
        logger.dim(f'Could not determine volume or chapter for "{lastItem}".')
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

  winsound.MessageBeep()
  Prompt.enter_to_exit()

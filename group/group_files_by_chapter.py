import os
import re
import shutil
import sys

from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from tqdm import tqdm

from _common import FILE_BLACKLIST
from mtprompt import Prompt

NUMBER_REGEX = r'\.?\s*(\d+(?:\.\d+)?)'
CHAPTER_REGEX = r'Ch(?:ap(?:ter)?)?|Ep(?:isode)?|Ep(?:ilogue)?|Sp(?:ecial)?'
CHAPTER_NUMBER_REGEX  = rf'(?:{CHAPTER_REGEX}){NUMBER_REGEX}'

def main():
  parent_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the files you want to group')

  process_parent_folder(parent_dir)

def process_parent_folder(
  parent_dir_path: str,
):
  files_to_process = []

  for item in os.listdir(parent_dir_path):
    item_path = os.path.join(parent_dir_path, item)
    if should_process_item(item_path):
      chapter = get_chapter(item)
      if not chapter:
        tqdm.write(logger.formatWarn(f'Skipping "{item}". Chapter number could not be inferred.'))
        continue

      output_path = os.path.join(parent_dir_path, f'Ch.{chapter.zfill(2)}')
      if not os.path.exists(output_path):
        os.makedirs(output_path)

      files_to_process.append((item_path, output_path, chapter))

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc = f'Processing "{parent_dir_path}"') as progress:
    for _ in executor.map(process_file, files_to_process):
      progress.update(1)

  logger.success(f'Finished grouping files in "{parent_dir_path}".\n')

def should_process_item(
  item_path: str,
):
  if not os.path.isfile(item_path):
    return False

  for pattern in FILE_BLACKLIST:
    if re.fullmatch(pattern, os.path.basename(item_path)):
      return False

  return True

def process_file(
  params: tuple,
):
  src, target_folder, chapter = params
  base, ext = os.path.splitext(os.path.basename(src))
  new_name = f'ch{chapter}_p{base}{ext}'
  dest = os.path.join(target_folder, new_name)

  counter = 1
  while os.path.exists(dest):
    dest = os.path.join(target_folder, f'ch{chapter}_p{base}_{counter:02d}{ext}')
    counter += 1
  shutil.move(src, dest)

def get_chapter(
  filename: str,
):
  ch_match = re.search(CHAPTER_NUMBER_REGEX, filename, re.IGNORECASE)
  chapter = ch_match.group(1) if ch_match else None
  return chapter

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

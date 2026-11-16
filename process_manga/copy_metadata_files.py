import mtsound
import os
import re
import shutil

from concurrent.futures import ThreadPoolExecutor, as_completed
from mtattr import Attr
from mtprompt import Prompt
from mtlogger import logger
from tqdm import tqdm

DESKTOP_INI = 'desktop.ini'
ICON_ICO = 'icon.ico'
NO_XML = '.noxml'
NO_MEDIA = '.nomedia'
COMIC_INFO = 'ComicInfo.xml'
COVER_JPG = 'cover.jpg'

HIDDEN_FILES = [ICON_ICO, COVER_JPG, COMIC_INFO, NO_XML, NO_MEDIA]
HIDDEN_SYSTEM_FILES = [DESKTOP_INI]
FILES_TO_COPY = HIDDEN_FILES + HIDDEN_SYSTEM_FILES


def main():
  a = Prompt.dir('Enter the path to the source directory')
  b = Prompt.dir('Enter the path to the destination directory')

  try:
    b_map = {sanitize_name(e.name): e.path for e in os.scandir(b) if e.is_dir()}
    dirs = [e for e in os.scandir(a) if e.is_dir()]

    tasks = []
    for entry in dirs:
      base = sanitize_name(entry.name)
      if base not in b_map:
        tqdm.write(f'No B match: {base}')
        continue

      tasks.append((entry.path, b_map[base]))

    with ThreadPoolExecutor() as executor:
      futures = [
        executor.submit(copy_directory, src, dst) for src, dst in tasks
      ]

      for future in tqdm(
        as_completed(futures), total=len(futures), desc='Copying files'
      ):
        try:
          future.result()
        except Exception as e:
          tqdm.write(logger.format_error(f'Error: {e}'))

    tqdm.write('Done.')
  except Exception as e:
    tqdm.write(logger.format_error(f'Error: {e}'))

  mtsound.notify()
  Prompt.enter_to_exit()


def sanitize_name(name: str):
  return re.sub(r'\s*[\(\{]\d{1,3}[\)\}]\s*$', '', name).strip()


def copy_directory(src_dir: str, dst_dir: str):
  try:
    for file_name in HIDDEN_SYSTEM_FILES:
      Attr.show(os.path.join(dst_dir, file_name), ['h', 's'])

    for file_name in HIDDEN_FILES:
      Attr.show(os.path.join(dst_dir, file_name))

    for file_name in FILES_TO_COPY:
      copy_file(os.path.join(src_dir, file_name), dst_dir, file_name)

    tqdm.write(logger.format_trace(f'Copied "{dst_dir}".'))

  finally:
    for file_name in HIDDEN_SYSTEM_FILES:
      Attr.hide(os.path.join(dst_dir, file_name), ['h', 's'])

    for file_name in HIDDEN_FILES:
      Attr.hide(os.path.join(dst_dir, file_name))


def copy_file(src: str, dst_dir: str, file_name: str):
  try:
    if os.path.isfile(src):
      shutil.copy(src, os.path.join(dst_dir, file_name))

  except Exception as e:
    tqdm.write(
      logger.format_error(f'Error copying {file_name} to {dst_dir}: {e}')
    )


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

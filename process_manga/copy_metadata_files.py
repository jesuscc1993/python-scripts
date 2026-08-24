import os
import re
import shutil
import winsound

from mtattr import Attr
from mtprompt import Prompt, logger
from tqdm import tqdm

DESKTOP_INI = 'desktop.ini'
ICON_ICO = 'icon.ico'
NO_XML = '.noxml'
NO_MEDIA = '.nomedia'
COMIC_INFO = 'ComicInfo.xml'
COVER_JPG = 'cover.jpg'

FILES_TO_COPY = [DESKTOP_INI, ICON_ICO, COVER_JPG, COMIC_INFO, NO_XML, NO_MEDIA]
HIDDEN_FILES = [ICON_ICO, NO_XML, NO_MEDIA]
HIDDEN_SYSTEM_FILES = [DESKTOP_INI]

def main():
  a = Prompt.dir('Enter the path to the source directory')
  b = Prompt.dir('Enter the path to the destination directory')

  try:
    b_map = {sanitize_name(e.name): e.path for e in os.scandir(b) if e.is_dir()}
    dirs = [e for e in os.scandir(a) if e.is_dir()]

    for entry in tqdm(dirs, desc='Copying'):
      base = sanitize_name(entry.name)
      if base not in b_map:
        tqdm.write(f'No B match: {base}')
        continue

      dst_dir = b_map[base]

      for file_name in HIDDEN_SYSTEM_FILES:
        Attr.show(os.path.join(dst_dir, file_name), ['h', 's'])
      for file_name in HIDDEN_FILES:
        Attr.show(os.path.join(dst_dir, file_name))

      for file_name in FILES_TO_COPY:
        copy_file(os.path.join(entry.path, file_name), dst_dir, file_name)

      for file_name in HIDDEN_SYSTEM_FILES:
        Attr.hide(os.path.join(dst_dir, file_name), ['h', 's'])
      for file_name in HIDDEN_FILES:
        Attr.hide(os.path.join(dst_dir, file_name))

    tqdm.write('Done.')
  except Exception as e:
    tqdm.write(f'Error: {e}')

  winsound.MessageBeep()
  Prompt.enter_to_exit()

def sanitize_name(name: str) -> str:
  return re.sub(r'\s*[\(\{]\d{1,3}[\)\}]\s*$', '', name).strip()

def copy_file(src: str, dst_dir: str, file_name: str):
  try:
    if os.path.isfile(src):
      shutil.copy(src, os.path.join(dst_dir, file_name))
      tqdm.write(f'Copied: {dst_dir} - {file_name}')
  except Exception as e:
    tqdm.write(f'Error copying {file_name} to {dst_dir}: {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
    Prompt.enter_to_exit()

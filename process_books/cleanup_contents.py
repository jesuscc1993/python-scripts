import os
import shutil
import tempfile
import zipfile

from bs4 import BeautifulSoup
from mtlogger import logger
from mtprompt import Prompt

ATTRS_TO_REMOVE = []
CLASSES_TO_REMOVE = []

REMOVE_BY_SELECTORS = [
  '[data-amznremoved]',
  '.mobispace'
]

REMOVE_EMPTY_TAGS = False

EXTENSIONS_TO_MATCH = ['.html', '.htm', '.xhtml']
SELF_CLOSING_TAGS = ['br', 'hr', 'img']

def main():
  ebook_path = Prompt.path('Enter the path to the ebook file/folder to clean')

  logger.log(f'Cleaning contents in "{ebook_path}"...')
  logger.hr()

  if (os.path.isfile(ebook_path)):
    process_ebook_file(ebook_path)
  else:
    process_ebook_dir(ebook_path)

  logger.hr()
  logger.success(f'Finished cleaning contents in "{ebook_path}".')

def process_ebook_file(ebook_file_path):
  ebook_file_name = os.path.basename(ebook_file_path)
  ebook_dir_path = os.path.join(tempfile.gettempdir(), ebook_file_name)
  os.makedirs(ebook_dir_path, exist_ok = True)

  try:
    unpack_ebook(ebook_file_path, ebook_dir_path)
    process_ebook_dir(ebook_dir_path)
    pack_ebook(ebook_file_path, ebook_dir_path)

  except Exception as ex:
    logger.error(f'An error occurred while processing "{ebook_file_name}":\n{ex}')

  finally:
    shutil.rmtree(ebook_dir_path, ignore_errors = True)

def unpack_ebook(ebook_file_path, ebook_dir_path):
  with zipfile.ZipFile(ebook_file_path, 'r') as archive:
    real_dir_path = os.path.realpath(ebook_dir_path)

    for member in archive.namelist():
      target_path = os.path.realpath(os.path.join(real_dir_path, member))
      if not target_path.startswith(real_dir_path + os.sep):
        raise ValueError(f'Unsafe path in archive: "{member}"')

    archive.extractall(ebook_dir_path)

def pack_ebook(ebook_file_path, ebook_dir_path):
  file_name = os.path.basename(ebook_file_path)
  tmp_path = os.path.join(tempfile.gettempdir(), f'{file_name}.tmp')

  try:
    with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as target:
      for root, _, files in os.walk(ebook_dir_path):
        for file in files:
          full_path = os.path.join(root, file)
          archive_name = os.path.relpath(full_path, ebook_dir_path).replace(os.sep, '/')
          target.write(full_path, archive_name)

    shutil.move(tmp_path, ebook_file_path)
  except Exception:
    if os.path.exists(tmp_path):
      os.remove(tmp_path)
    raise

def process_ebook_dir(ebook_dir_path):
  for root, _, files in os.walk(ebook_dir_path):
    for file in files:
      if any(file.lower().endswith(ext) for ext in EXTENSIONS_TO_MATCH):
        process_html_file(os.path.join(root, file))
      elif file.lower().endswith('.epub'):
        process_ebook_file(os.path.join(root, file))

def process_html_file(html_path):
  file_name = os.path.basename(html_path)

  try:
    with open(html_path, 'rb') as html_file:
      content = html_file.read()

    soup = BeautifulSoup(content, 'html.parser')
    was_changed = clean_soup(soup)

    if not was_changed:
      logger.trace(f'Skipping "{file_name}". Nothing to clean.')
      return

    with open(html_path, 'wb') as html_file:
      html_file.write(str(soup).encode('utf-8'))

    logger.success(f'Cleaned "{file_name}".')

  except Exception as ex:
    logger.error(f'An error occurred while processing "{file_name}":\n{ex}')

def clean_soup(
  soup: BeautifulSoup,
):
  changed = False

  for attr in ATTRS_TO_REMOVE:
    for tag in soup.find_all(attrs = {attr: True}):
      del tag[attr]
      changed = True

  for class_name in CLASSES_TO_REMOVE:
    for tag in soup.find_all(class_ = class_name):
      classes = [name for name in tag.get('class', []) if name != class_name]
      if classes:
        tag['class'] = classes
      else:
        del tag['class']
      changed = True

  tags_to_delete = []

  for selector in REMOVE_BY_SELECTORS:
    tags_to_delete += soup.select(selector)

  if REMOVE_EMPTY_TAGS:
    tags_to_delete += [
      tag for tag in soup.find_all()
      if (
        tag.name not in SELF_CLOSING_TAGS and
        not tag.find(True) and
        not tag.get_text().strip()
      )
    ]

  for tag in tags_to_delete:
    tag.decompose()
    changed = True

  return changed

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

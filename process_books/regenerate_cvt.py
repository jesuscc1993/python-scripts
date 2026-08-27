import os
import re
import shutil
import sys
import tempfile
import zipfile

from io import BytesIO
from PIL import Image
from mtlogger import logger
from mtprompt import Prompt

BOOK_EXTENSIONS = ['.epub']
IMAGES_DIR = 'OEBPS/images'
MAX_W = 200
MAX_H = 300
CVI_PATTERN = re.compile(r'(.*)_cvi(_|\.)', re.IGNORECASE)
CVT_PATTERN = re.compile(r'(.*)_cvt(_|\.)', re.IGNORECASE)

def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your manga'
    )

  logger.log(f'Generating cover thumbs in "{parent_dir}"...')
  logger.hr()

  for root, _, files in os.walk(parent_dir):
    for file_name in files:
      if file_name.lower().endswith(tuple(BOOK_EXTENSIONS)):
        process_file(os.path.join(root, file_name))
        logger.hr()

  logger.success(f'Finished generating cover thumbs in "{parent_dir}".')

def process_file(
  file_path: str,
):
  file_name = os.path.basename(file_path)

  try:
    with zipfile.ZipFile(file_path, 'r') as archive:
      names = archive.namelist()
      cvt_names = [name for name in names if is_cover_thumb(name)]

      if not cvt_names:
        logger.trace(f'Skipping "{file_name}". No cover thumbnail found.')
        return

      updates = {}
      for cvt_name in cvt_names:
        cvi_name = get_cover_image_name(cvt_name, names)
        if not cvi_name:
          logger.warn(f'Skipping "{cvt_name}". No matching cover image found.')
          continue

        updates[cvt_name] = generate_thumb(archive, cvi_name, cvt_name)

    if not updates:
      return

    tmp_path = os.path.join(tempfile.gettempdir(), f'{file_name}.tmp')
    try:
      with zipfile.ZipFile(file_path, 'r') as source, zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
          data = updates.get(item.filename, None)
          target.writestr(item, data if data is not None else source.read(item.filename))

      shutil.move(tmp_path, file_path)
    except Exception:
      if os.path.exists(tmp_path):
        os.remove(tmp_path)
      raise

    logger.success(f'Regenerated {len(updates)} cover thumb(s) in "{file_name}".')

  except Exception as ex:
    logger.error(f'An error occurred while processing "{file_name}":\n{ex}')

def is_cover_thumb(
  name: str,
):
  return (
    os.path.dirname(name).lower().endswith(IMAGES_DIR.lower()) and
    bool(CVT_PATTERN.match(os.path.basename(name)))
  )

def is_cover(
  name: str,
):
  return (
    os.path.dirname(name).lower().endswith(IMAGES_DIR.lower()) and
    bool(CVI_PATTERN.match(os.path.basename(name)))
  )

def get_cover_image_name(
  cvt_name: str,
  names: list[str],
):
  match = CVT_PATTERN.match(cvt_name)
  if not match:
    return None

  base = match.group(1)
  dir_name = os.path.dirname(cvt_name)
  covers = [name for name in names if is_cover(name) and os.path.dirname(name) == dir_name]

  for name in covers:
    if CVI_PATTERN.match(name).group(1) == base:
      return name

  return covers[0] if len(covers) == 1 else None

def generate_thumb(
  archive: zipfile.ZipFile,
  cvi_name: str,
  cvt_name: str,
):
  with archive.open(cvi_name) as cvi_file:
    img = Image.open(BytesIO(cvi_file.read()))
    img.load()

  img.thumbnail((MAX_W, MAX_H), Image.LANCZOS)

  image_format = get_image_format(cvt_name, img)
  if image_format == 'JPEG' and img.mode != 'RGB':
    img = img.convert('RGB')

  buffer = BytesIO()
  img.save(buffer, format = image_format)
  return buffer.getvalue()

def get_image_format(
  name: str,
  img: Image.Image,
):
  ext = os.path.splitext(name)[1].lower()
  return Image.registered_extensions().get(ext, img.format)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

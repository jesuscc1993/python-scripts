import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from io import BytesIO
from PIL import Image
from mtlogger import logger
from mtprompt import Prompt

BOOK_EXTENSIONS = ['.epub']
COVER_EXTENSIONS = ['jpeg', 'jpg', 'png', 'webp']
CONTAINER_PATH = 'META-INF/container.xml'
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
      'Enter the path to the directory containing your books'
    )

  logger.log(f'Updating covers in "{parent_dir}"...')
  logger.hr()

  for root, _, files in os.walk(parent_dir):
    for file_name in files:
      if file_name.lower().endswith(tuple(BOOK_EXTENSIONS)):
        process_file(os.path.join(root, file_name))
        logger.hr()

  logger.success(f'Finished updating covers in "{parent_dir}".')

def process_file(
  file_path: str,
):
  file_name = os.path.basename(file_path)
  external_cover_path = find_external_cover(file_path)

  try:
    with zipfile.ZipFile(file_path, 'r') as archive:
      names = archive.namelist()
      pairs = get_cover_pairs(archive, names)

      if not pairs:
        logger.trace(f'Skipping "{file_name}". No cover found.')
        return

      updates = {}
      for pair in pairs:
        cvi_name = pair['cvi_name']
        cvt_name = pair['cvt_name']

        if external_cover_path:
          cover_bytes = load_cover_image(external_cover_path, cvi_name)
          updates[cvi_name] = cover_bytes
          logger.log(f'Replacing cover "{cvi_name}" with "{os.path.basename(external_cover_path)}".')
        elif cvt_name:
          with archive.open(cvi_name) as cvi_file:
            cover_bytes = cvi_file.read()
        else:
          continue

        if cvt_name:
          updates[cvt_name] = generate_thumb(cover_bytes, cvt_name)

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

    logger.success(f'Updated {len(updates)} cover file(s) in "{file_name}".')

  except Exception as ex:
    logger.error(f'An error occurred while processing "{file_name}":\n{ex}')

def find_external_cover(
  file_path: str,
):
  dir_name = os.path.dirname(file_path)
  base_name = os.path.splitext(os.path.basename(file_path))[0]

  for ext in COVER_EXTENSIONS:
    candidate_path = os.path.join(dir_name, f'{base_name}.{ext}')
    if os.path.isfile(candidate_path):
      return candidate_path

  return None

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

def find_cover_by_opf(
  archive: zipfile.ZipFile,
  names: list[str],
):
  if CONTAINER_PATH not in names:
    return None

  with archive.open(CONTAINER_PATH) as container_file:
    container_root = ET.fromstring(container_file.read())

  rootfile = container_root.find('.//{*}rootfile')
  opf_path = rootfile.get('full-path') if rootfile is not None else None
  if not opf_path or opf_path not in names:
    return None

  with archive.open(opf_path) as opf_file:
    opf_root = ET.fromstring(opf_file.read())

  for item in opf_root.findall('.//{*}item'):
    if 'cover-image' in item.get('properties', '').split():
      href = item.get('href')
      if not href:
        continue

      cover_path = os.path.normpath(os.path.join(os.path.dirname(opf_path), href)).replace(os.sep, '/')
      if cover_path in names:
        return cover_path

  return None

def get_cover_pairs(
  archive: zipfile.ZipFile,
  names: list[str],
):
  cvt_names = [name for name in names if is_cover_thumb(name)]
  handled_cvis = set()
  handled_cvts = set()
  pairs = []

  for cvt_name in cvt_names:
    cvi_name = get_cover_image_name(cvt_name, names)
    if cvi_name:
      pairs.append({ 'cvi_name': cvi_name, 'cvt_name': cvt_name })
      handled_cvis.add(cvi_name)
      handled_cvts.add(cvt_name)

  opf_cover_name = find_cover_by_opf(archive, names)
  if opf_cover_name and opf_cover_name not in handled_cvis:
    dir_name = os.path.dirname(opf_cover_name)
    candidate_cvts = [
      name for name in cvt_names
      if os.path.dirname(name) == dir_name and name not in handled_cvts
    ]
    pairs.append({
      'cvi_name': opf_cover_name,
      'cvt_name': candidate_cvts[0] if len(candidate_cvts) == 1 else None,
    })

  return pairs

def load_cover_image(
  image_path: str,
  cvi_name: str,
):
  img = Image.open(image_path)
  img.load()

  image_format = get_image_format(cvi_name, img)
  if image_format == 'JPEG' and img.mode != 'RGB':
    img = img.convert('RGB')

  buffer = BytesIO()
  img.save(buffer, format = image_format)
  return buffer.getvalue()

def generate_thumb(
  cover_bytes: bytes,
  cvt_name: str,
):
  img = Image.open(BytesIO(cover_bytes))
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

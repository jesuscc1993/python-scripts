import requests

from PIL import Image
from io import BytesIO
from mtlogger import logger
from pathlib import Path

from _constants import COVER_URL_MAP

def download_assets_for_app_id(
  steam_app_id: str,
  dest_dir: str,
  filename_id: str = None,
):
  filename_id = filename_id or steam_app_id
  Path(dest_dir).mkdir(parents = True, exist_ok = True)
  for _, data in COVER_URL_MAP.items():
    url = data['url'].format(steam_app_id)
    filename = data['dest'].format(filename_id)
    download_asset_for_app_id(url, Path(dest_dir) / filename, data.get('size'))

def download_asset_for_app_id(
  url: str,
  dest: Path,
  size: list = None,
):
  if Path(dest).exists():
    logger.trace(f'Skipping {Path(dest).name}: already exists')
    return
  response = requests.get(url)
  response.raise_for_status()
  save_asset(response.content, dest, size)

def save_asset(
  content: bytes,
  filepath: Path,
  size: list = None,
):
  try:
    img = Image.open(BytesIO(content))
    if size:
      img = img.resize(size, Image.LANCZOS)
    img.save(filepath)
    logger.success(f'Saved "{filepath}"')
  except Exception as ex:
    logger.error(f'Could not save {filepath}:\n{ex}')

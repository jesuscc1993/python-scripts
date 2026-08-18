import os
import requests

from PIL import Image
from dotenv import load_dotenv
from io import BytesIO
from mtlogger import logger
from pathlib import Path

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

COVER_H = os.environ.get('COVER_H')
COVER_W = os.environ.get('COVER_W')
HEADER_H = os.environ.get('HEADER_H')
HEADER_W = os.environ.get('HEADER_W')

COVER_H = int(COVER_H) if COVER_H else None
COVER_W = int(COVER_W) if COVER_W else None
HEADER_H = int(HEADER_H) if HEADER_H else None
HEADER_W = int(HEADER_W) if HEADER_W else None

COVER_URL_MAP = {
  'header': {
    'url': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/header.jpg',
    'dest': '{}.jpg',
    'size': [HEADER_W, HEADER_H] if HEADER_W and HEADER_H else None
  },
  'library': {
    'url': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900_2x.jpg',
    'dest': '{}p.jpg',
    'size': [COVER_W, COVER_H] if COVER_W and COVER_H else None
  }
}

HEADER_SIZE = COVER_URL_MAP['header']['size']
COVER_SIZE = COVER_URL_MAP['library']['size']

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

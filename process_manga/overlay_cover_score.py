
import math
import os
import re
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm
from xml.etree import ElementTree

COMIC_INFO_FILENAME = 'ComicInfo.xml'
COVER_NAMES = [
  'cover.jpg',
  'cover.png',
  'cover.webp',
]
COVER_BAK_EXT = '.bak'
COVER_W = 212
COVER_H = 318

OVERLAY_PADDING = 8
OVERLAY_MARGIN = 8
OVERLAY_RADIUS = 8

FONT_NAME = 'Roboto-Regular.ttf'
FONT_SIZE = 31

FG_GRAY = '#333333'
BG_LOWEST = '#FF9191'
BG_LOW = '#FFCC80'
BG_MEDIUM = '#FFF480'
BG_HIGH = '#D6E58A'
BG_HIGHEST = '#A4E0A4'

VALUE_LOW = 60
VALUE_MEDIUM = 65
VALUE_HIGH = 70
VALUE_HIGHEST = 80

def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your manga'
    )

  font = ImageFont.truetype(find_font(FONT_NAME), FONT_SIZE)

  dirs_to_process = []
  for entry in os.scandir(parent_dir):
    if entry.is_dir():
      dirs_to_process.append(entry.path)

  with ThreadPoolExecutor() as executor, tqdm(total = len(dirs_to_process), desc = f'Processing "{parent_dir}"') as progress:
    for _ in executor.map(lambda dir: process_dir(dir, font), dirs_to_process):
      progress.update(1)

  logger.success(f'Finished overlaying scores in "{parent_dir}".')

def tqdm_dim(
  msg: str,
):
  tqdm.write(logger.formatTrace(msg))

def find_font(
  name: str,
):
  user_fonts = os.path.join(os.environ.get('LOCALAPPDATA'), 'Microsoft', 'Windows', 'Fonts', name)
  if os.path.exists(user_fonts):
    return user_fonts

  system_fonts = os.path.join(os.environ.get('WINDIR'), 'Fonts', name)
  if os.path.exists(system_fonts):
    return system_fonts

  return None

def find_cover(
  dir: str,
  is_backup = False,
):
  for cover_name in COVER_NAMES:
    path = get_cover_path(dir, cover_name, is_backup)
    if os.path.isfile(path):
      return path
  return None

def get_cover_path(
  dir: str,
  cover_name: str,
  is_backup = False,
):
  name, ext = os.path.splitext(cover_name)
  path = os.path.join(dir, name + (COVER_BAK_EXT if is_backup else '') + ext)
  return path

def process_dir(
  dir: str,
  font: ImageFont.FreeTypeFont,
):
  dir_name = os.path.basename(dir)
  cover_img_path = find_cover(dir)
  cover_img_bak_path = find_cover(dir, is_backup=True)

  if cover_img_path is None and cover_img_bak_path is None:
    tqdm_dim(f'Skipping "{dir_name}". No cover found.')
    return

  if cover_img_bak_path is None:
    cover_img_bak_path = get_cover_path(dir, os.path.basename(cover_img_path), is_backup=True)

  score_match = re.search(r'\{(\d{1,3})?\}', os.path.basename(dir))
  score = int(score_match.group(1)) if score_match else None
  if score is None:
    score = read_score_from_comic_info(dir)
  if score is None:
    tqdm_dim(f'Skipping "{dir_name}". Score could not be inferred.')
    return

  process_cover(dir, cover_img_path, cover_img_bak_path, score, font)

def read_score_from_comic_info(
  dir: str,
):
  comic_info_path = os.path.join(dir, COMIC_INFO_FILENAME)
  if not os.path.isfile(comic_info_path):
    return None

  try:
    rating = ElementTree.parse(comic_info_path).getroot().findtext('CommunityRating')
    return round(float(rating) * 20) if rating else None
  except Exception:
    return None

def process_cover(
  dir: str,
  cover_img_path: str,
  cover_img_bak_path: str,
  score: int,
  font: ImageFont.FreeTypeFont,
):
  if not os.path.exists(cover_img_bak_path):
    shutil.copy(cover_img_path, cover_img_bak_path)
    os.remove(cover_img_path)

  processed_cover_img_path = os.path.join(dir, COVER_NAMES[0])
  img = Image.open(cover_img_bak_path).convert('RGBA')
  img = resize_cover(img, COVER_W, COVER_H)
  img = overlay_score(img, score, font)
  img.save(processed_cover_img_path, quality=100)

  tqdm.write(logger.formatDebug(f'Applied score overlay to "{os.path.basename(dir)}".'))

def resize_cover(
  img: Image.Image,
  target_w: int,
  target_h: int,
):
  scale = max(target_w / img.width, target_h / img.height)
  img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
  left = (img.width - target_w) // 2
  top = (img.height - target_h) // 2
  return img.crop((left, top, left + target_w, top + target_h))

def overlay_score(
  img: Image.Image,
  score: int,
  font: ImageFont.FreeTypeFont,
):
  text = format_score(score)
  bg_color = get_score_color(score)

  overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
  draw = ImageDraw.Draw(overlay)

  text_reservation = draw.textbbox((0, 0), text, font=font)
  text_w = text_reservation[2] - text_reservation[0]
  text_h = text_reservation[3] - text_reservation[1]
  text_offset_x = -text_reservation[0]
  text_offset_y = -text_reservation[1]

  canvas_w = text_w + OVERLAY_PADDING * 2
  canvas_h = text_h + OVERLAY_PADDING * 2
  x = img.width - canvas_w - OVERLAY_MARGIN - 1
  y = OVERLAY_MARGIN

  draw.rounded_rectangle([x, y, x + canvas_w, y + canvas_h], radius=OVERLAY_RADIUS, fill=bg_color)
  draw.text((x + OVERLAY_PADDING + text_offset_x, y + OVERLAY_PADDING + text_offset_y), text, font=font, fill=FG_GRAY)

  return Image.alpha_composite(img, overlay).convert('RGB')

def format_score(
  score: int,
):
  return f'{math.ceil(score)}%'
  # return f'{math.ceil(score) / 10:.1f}'

def get_score_color(
  score: int,
):
  if score < VALUE_LOW: return BG_LOWEST
  if score < VALUE_MEDIUM: return BG_LOW
  elif score < VALUE_HIGH: return BG_MEDIUM
  elif score < VALUE_HIGHEST: return BG_HIGH
  return BG_HIGHEST

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit(timeout=True)


import os
import re
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm

COVER_NAME = 'cover.jpg'
COVER_BAK_NAME = '.bak'.join(list(os.path.splitext(COVER_NAME)))
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

def tqdm_dim(msg):
  tqdm.write(logger.formatTrace(msg))

def find_font(name):
  user_fonts = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts', name)
  if os.path.exists(user_fonts):
    return user_fonts

  system_fonts = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', name)
  if os.path.exists(system_fonts):
    return system_fonts

  return None

def process_dir(dir, font):
  dir_name = os.path.basename(dir)
  cover_img = os.path.join(dir, COVER_NAME)

  if not os.path.isfile(cover_img):
    tqdm_dim(f'Skipping "{dir_name}". No cover found.')
    return

  score_match = re.search(r'\{(\d{1,3})?\}', os.path.basename(dir))
  score = int(score_match.group(1)) if score_match else None
  if score is None:
    tqdm_dim(f'Skipping "{dir_name}". Score could not be inferred.')
    return

  process_cover(dir, cover_img, score, font)

def process_cover(dir, cover_img, score, font):
  cover_bak_img = os.path.join(dir, COVER_BAK_NAME)
  if not os.path.exists(cover_bak_img):
    shutil.copy(cover_img, cover_bak_img)

  shutil.copy(cover_bak_img, cover_img)
  img = Image.open(cover_img).convert('RGBA')
  img = resize_cover(img, COVER_W, COVER_H)
  img = overlay_score(img, score, font)
  img.save(cover_img, quality=100)

  tqdm.write(logger.formatDebug(f'Applied score overlay to "{os.path.basename(dir)}".'))

def resize_cover(img, target_w, target_h):
  scale = max(target_w / img.width, target_h / img.height)
  img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
  left = (img.width - target_w) // 2
  top = (img.height - target_h) // 2
  return img.crop((left, top, left + target_w, top + target_h))

def overlay_score(img, score, font):
  text = f'{score}%'
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

def get_score_color(score):
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

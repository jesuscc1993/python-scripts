import colorsys
import hashlib
import os
import re
import sys

from itertools import combinations
from PIL import Image, ImageDraw, ImageFont
from mtfont import Font, SegoeFontName
from mtlogger import logger
from mtprompt import Prompt

BOOK_EXTENSIONS = ['.epub']
COVER_EXT = '.webp'

COVER_W = 200
COVER_H = 300

SMALL_TEXT_H = 24
TITLE_H = 76
SERIES_H = SMALL_TEXT_H
AUTHOR_H = SMALL_TEXT_H
CENTER_H = COVER_H - TITLE_H - SMALL_TEXT_H - AUTHOR_H

FONT_PATH = Font.find_by_name(SegoeFontName.SEMIBOLD)
TITLE_FONT_SIZE = 20
SERIES_FONT_SIZE = 16
INDEX_FONT_SIZE = 96
WRITER_FONT_SIZE = 16
MAX_TITLE_LINES = 3
MAX_TEXT_TO_SIZE_RATIO = 0.9
SAME_FONT_LINE_SPACING = 0.8

BG_COLOR = (0, 0, 0)
PRIMARY_FG_COLOR = (255, 255, 255)
SECONDARY_FG_COLOR = (171, 171, 171)
HUE_SATURATION = 0.55
HUE_VALUE = 0.85

# expected file name format: [Author] [Series] [Number] Title
# Author, Series and Number are all optional, but each one requires the ones before it
TAG_PATTERN = re.compile(r'^\[([^\]]+)\]\s*')

def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your books'
    )

  logger.log(f'Generating covers in "{parent_dir}"...')
  logger.hr()

  for root, _, files in os.walk(parent_dir):
    for file_name in files:
      if file_name.lower().endswith(tuple(BOOK_EXTENSIONS)):
        process_file(os.path.join(root, file_name))

  logger.hr()
  logger.success(f'Finished generating covers in "{parent_dir}".')

def process_file(
  file_path: str,
):
  file_name = os.path.basename(file_path)
  stem = os.path.splitext(file_name)[0]

  book_data = parse_book_name(stem)
  if not book_data['title']:
    logger.warn(f'Skipping "{file_name}". No title found.')
    return

  img = generate_cover(book_data, stem)

  cover_path = os.path.join(os.path.dirname(file_path), f'{stem}{COVER_EXT}')
  img.save(cover_path, quality = 95)

  logger.success(f'Generated cover for "{file_name}".')

def parse_book_name(
  name: str,
):
  remaining = name

  author = None
  series = None
  number = None

  match = TAG_PATTERN.match(remaining)
  if match:
    author = match.group(1).strip()
    remaining = remaining[match.end():]

    match = TAG_PATTERN.match(remaining)
    if match:
      series = match.group(1).strip()
      remaining = remaining[match.end():]

      match = TAG_PATTERN.match(remaining)
      if match:
        number = match.group(1).strip()
        remaining = remaining[match.end():]

  title = re.sub(r'\[.*?\]', '', remaining).strip()
  title = re.sub(r'\s+', ' ', title)

  return { 'author': author, 'series': series, 'number': number, 'title': title }

def generate_cover(
  book_data: dict,
  hash_source: str,
):
  bg_color = get_hash_color(hash_source)
  img = Image.new('RGB', (COVER_W, COVER_H), bg_color)
  draw = ImageDraw.Draw(img)

  draw_title_section(draw, book_data)
  draw_series_section(draw, book_data)
  draw_index_section(draw, book_data)
  draw_writer_section(draw, book_data)

  return img

def get_hash_color(
  text: str,
):
  digest = hashlib.sha256(text.encode('utf-8')).digest()
  hue = digest[0] / 255
  r, g, b = colorsys.hsv_to_rgb(hue, HUE_SATURATION, HUE_VALUE)

  return (round(r * 255), round(g * 255), round(b * 255))

def measure(
  draw: ImageDraw.ImageDraw,
  text: str,
  font: ImageFont.FreeTypeFont,
):
  bbox = draw.textbbox((0, 0), text, font = font)
  return bbox[2] - bbox[0], bbox[3] - bbox[1]

def line_height(
  font: ImageFont.FreeTypeFont,
):
  ascent, descent = font.getmetrics()
  return ascent + descent

def draw_text(
  draw: ImageDraw.ImageDraw,
  text: str,
  font: ImageFont.FreeTypeFont,
  x: int,
  y: int,
  fill,
):
  bbox = draw.textbbox((0, 0), text, font = font)
  draw.text((x - bbox[0], y), text, font = font, fill = fill)

def wrap_lines(
  draw: ImageDraw.ImageDraw,
  text: str,
  font: ImageFont.FreeTypeFont,
  max_width: int,
):
  words = text.split()
  lines = []
  current = ''

  for word in words:
    candidate = f'{current} {word}'.strip()
    width, _ = measure(draw, candidate, font)

    if width <= max_width or not current:
      current = candidate
    else:
      lines.append(current)
      current = word

  if current:
    lines.append(current)

  return lines

def ellipsize(
  draw: ImageDraw.ImageDraw,
  text: str,
  font: ImageFont.FreeTypeFont,
  max_width: int,
):
  if measure(draw, text, font)[0] <= max_width:
    return text

  while text and measure(draw, f'{text}…', font)[0] > max_width:
    text = text[:-1]

  return f'{text}…' if text else '…'

def balance_lines(
  draw: ImageDraw.ImageDraw,
  words: list,
  font: ImageFont.FreeTypeFont,
  max_width: int,
  num_lines: int,
):
  if num_lines < 2 or len(words) < num_lines:
    return None

  best_split = None
  best_score = None

  for cuts in combinations(range(1, len(words)), num_lines - 1):
    points = (0,) + cuts + (len(words),)
    lines = [' '.join(words[points[i]:points[i + 1]]) for i in range(num_lines)]
    widths = [measure(draw, line, font)[0] for line in lines]

    if any(width > max_width for width in widths):
      continue

    score = max(widths) - min(widths)
    if best_score is None or score < best_score:
      best_score = score
      best_split = lines

  return best_split

def try_fit_lines(
  draw: ImageDraw.ImageDraw,
  text: str,
  font: ImageFont.FreeTypeFont,
  max_width: int,
  max_lines: int,
):
  if measure(draw, text, font)[0] <= max_width:
    return [text]

  words = text.split()
  for num_lines in range(2, max_lines + 1):
    lines = balance_lines(draw, words, font, max_width, num_lines)
    if lines:
      return lines

  return None

def block_height(
  font: ImageFont.FreeTypeFont,
  num_lines: int,
):
  height = line_height(font)
  return height + height * SAME_FONT_LINE_SPACING * (num_lines - 1)

def fit_text_lines(
  draw: ImageDraw.ImageDraw,
  text: str,
  max_width: int,
  max_height: int,
  max_lines: int,
  max_size: int,
):
  for size in range(max_size, 0, -1):
    font = Font.load_by_path(FONT_PATH, size)
    lines = try_fit_lines(draw, text, font, max_width, max_lines)

    if lines and block_height(font, len(lines)) <= max_height:
      return lines, font

  font = Font.load_by_path(FONT_PATH, 1)
  lines = wrap_lines(draw, text, font, max_width)[:max_lines]
  if lines:
    lines[-1] = ellipsize(draw, lines[-1], font, max_width)

  return lines, font

def fit_single_line(
  draw: ImageDraw.ImageDraw,
  text: str,
  max_width: int,
  max_height: int,
  max_size: int,
):
  for size in range(max_size, 0, -1):
    font = Font.load_by_path(FONT_PATH, size)
    width, _ = measure(draw, text, font)

    if width <= max_width and line_height(font) <= max_height:
      return font

  return Font.load_by_path(FONT_PATH, 1)

def draw_black_box(
  draw: ImageDraw.ImageDraw,
  y0: int,
  height: int,
):
  draw.rectangle([0, y0, COVER_W, y0 + height], fill = BG_COLOR)

def draw_line_block(
  draw: ImageDraw.ImageDraw,
  blocks: list,
  y_offset: int,
  area_height: int,
):
  if not blocks:
    return

  line_heights = [line_height(font) for _, font, _ in blocks]
  advances = [
    line_heights[i] * (SAME_FONT_LINE_SPACING if blocks[i][1] is blocks[i + 1][1] else 1)
    for i in range(len(blocks) - 1)
  ]
  total_height = sum(advances) + line_heights[-1]
  y = y_offset + (area_height - total_height) // 2

  for i, (text, font, fill) in enumerate(blocks):
    width, _ = measure(draw, text, font)
    x = (COVER_W - width) // 2
    draw_text(
      draw,
      text,
      font,
      x,
      y,
      fill
    )
    if i < len(advances):
      y += advances[i]

def draw_small_text(
  draw: ImageDraw.ImageDraw,
  text: str,
  y_offset: int,
  color: tuple,
  max_size: int,
):
  if not text:
    return

  draw_black_box(
    draw,
    y_offset,
    SMALL_TEXT_H
  )

  max_width = COVER_W * MAX_TEXT_TO_SIZE_RATIO
  max_height = SMALL_TEXT_H * MAX_TEXT_TO_SIZE_RATIO

  font = fit_single_line(draw, text, max_width, max_height, max_size)
  line = ellipsize(draw, text, font, max_width)
  width, _ = measure(draw, line, font)
  x = (COVER_W - width) // 2
  y = y_offset + (SMALL_TEXT_H - line_height(font)) // 2

  draw_text(
    draw,
    line,
    font,
    x,
    y,
    color
  )

def draw_title_section(
  draw: ImageDraw.ImageDraw,
  book_data: dict,
):
  title = book_data['title']
  series = book_data['series']

  draw_black_box(
    draw,
    0,
    TITLE_H
  )

  max_width = COVER_W * MAX_TEXT_TO_SIZE_RATIO
  max_height = TITLE_H * MAX_TEXT_TO_SIZE_RATIO

  title_lines, title_font = fit_text_lines(
    draw,
    title,
    max_width,
    max_height,
    MAX_TITLE_LINES,
    TITLE_FONT_SIZE
  )
  blocks = [(line, title_font, PRIMARY_FG_COLOR) for line in title_lines]

  y_offset = SERIES_H * (MAX_TITLE_LINES - len(title_lines) + 1) * .1 if series else 0
  print('y_offset', y_offset)
  draw_line_block(
    draw,
    blocks,
    y_offset,
    TITLE_H
  )

def draw_series_section(
  draw: ImageDraw.ImageDraw,
  book_data: dict,
):
  draw_small_text(
    draw,
    book_data['series'],
    TITLE_H,
    SECONDARY_FG_COLOR,
    SERIES_FONT_SIZE
  )

def draw_index_section(
  draw: ImageDraw.ImageDraw,
  book_data: dict,
):
  number = book_data['number']
  y_offset = TITLE_H + AUTHOR_H

  if not number:
    return

  max_width = COVER_W * MAX_TEXT_TO_SIZE_RATIO
  max_height = CENTER_H * MAX_TEXT_TO_SIZE_RATIO

  font = fit_single_line(draw, number, max_width, max_height, INDEX_FONT_SIZE)
  width, _ = measure(draw, number, font)
  x = (COVER_W - width) // 2
  y = y_offset + (CENTER_H - line_height(font)) // 2

  draw_text(
    draw,
    number,
    font,
    x,
    y,
    BG_COLOR
  )

def draw_writer_section(
  draw: ImageDraw.ImageDraw,
  book_data: dict,
):
  draw_small_text(
    draw,
    book_data['author'],
    TITLE_H + AUTHOR_H + CENTER_H,
    PRIMARY_FG_COLOR,
    WRITER_FONT_SIZE
  )

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

import ctypes
import math
import os
import shutil
import stat
import sys
import win32con
import win32gui
import win32ui
import winsound

from PIL import Image, ImageDraw, ImageFont
from mtlogger import logger
from mtprompt import Prompt

from _constants import DESKTOP_INI_FILENAME, HIDDEN_SYSTEM_FILE_ATTRS, ICO_FILENAME, MAX_ICO_SIZE, PREFERRED_ENCODING
from _common import add_file_attrs, get_ini_icon, hide_file, read_ini, set_folder_icon, show_file, write_hidden_file

DEBUG = False
FORCE_RECALCULATE = False
OVERRIDE = False
OVERLAY_SMALLER_THAN_GB = False

FONT_NAME = 'segoeuib.ttf'
ICO_BAK_FILENAME = 'icon.bak.ico'
DIR_SIZE_FILENAME = 'dir_file_size.txt'
EXCLUSION_FILE = '.noscan'

SIZE_256 = 256
VALUE_FONT_SIZE_256 = 40
UNITS_FONT_SIZE_256 = int(VALUE_FONT_SIZE_256 * 0.775)

SIZE_48 = 48
VALUE_FONT_SIZE_48 = 14
UNITS_FONT_SIZE_48 = int(VALUE_FONT_SIZE_48 * 0.8)

BG_COLOR = (25, 25, 25, 255)
VALUE_COLOR = (255, 255, 255, 255)
UNITS_COLOR = (192, 192, 192, 255)

def main():
  if len(sys.argv) > 1:
    parent_path = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 1
  else:
    parent_path = Prompt.dir(
      'Enter the path to the directory containing the exes you want to process'
    )
    depth = Prompt.int(
      'Enter the depth for processing subfolders',
      default=1
    )

  parent_path = os.path.abspath(parent_path)

  if depth == 0:
    process_dir(parent_path, override_existing=OVERRIDE)
  else:
    parent_depth = parent_path.rstrip(os.sep).count(os.sep)

    for root, dirs, _ in os.walk(parent_path):
      current_depth = root.rstrip(os.sep).count(os.sep) - parent_depth
      if current_depth >= depth:
        dirs.clear()
        continue

      dirs[:] = [d for d in dirs if not should_skip_dir(os.path.join(root, d))]

      for dir_name in dirs:
        child_path = os.path.join(root, dir_name)
        logger.log()
        process_dir(child_path, override_existing=OVERRIDE)

  winsound.MessageBeep()
  logger.success(f'Finished setting icons for "{parent_path}".', prefix_newline=True)

def should_skip_dir(
  dir_path: str,
):
  should_skip = is_hidden(dir_path) or has_exclusion_file(dir_path)
  if should_skip:
    logger.trace(f'  Skipping "{dir_path}". Directory is hidden or contains a {EXCLUSION_FILE} file.')
  return should_skip

def is_hidden(
  path: str,
):
  return os.lstat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN

def has_exclusion_file(
  path: str,
):
  return os.path.exists(os.path.join(path, EXCLUSION_FILE))

def process_dir(
  dir_path: str,
  override_existing = False,
):
  try:
    ini_path = os.path.join(dir_path, DESKTOP_INI_FILENAME)
    config, _ = read_ini(ini_path)
    ico_config = get_ini_icon(config)
    if not ico_config:
      logger.trace(f'  Skipping "{dir_path}". No folder icon is set.')
      return

    if ',' in ico_config:
      ico_path, ico_index = ico_config.rsplit(',', 1)
    else:
      ico_path = ico_config
      ico_index = '0'

    new_ico_name = ICO_FILENAME
    new_ico_path = os.path.join(dir_path, new_ico_name)
    bak_ico_path = os.path.join(dir_path, ICO_BAK_FILENAME)
    dir_size_path = os.path.join(dir_path, DIR_SIZE_FILENAME)
    override = override_existing or new_ico_name not in ico_path

    if not FORCE_RECALCULATE and not override_existing and os.path.exists(new_ico_path) and os.path.exists(dir_size_path):
      if os.path.getmtime(new_ico_path) > os.path.getmtime(dir_size_path):
        logger.trace(f'  Skipping "{dir_path}". Icon is up to date.')
        return

    ico_path_lower = ico_path.lower()

    if ICO_FILENAME in ico_path_lower and os.path.exists(bak_ico_path):
      ico_path = ico_path.replace(ICO_FILENAME, ICO_BAK_FILENAME)
      ico_path_lower = ico_path.lower()
    elif '.ico' in ico_path_lower and ICO_FILENAME not in ico_path_lower:
      shutil.copy2(os.path.join(dir_path, ico_path), bak_ico_path)
      hide_file(bak_ico_path)

    ico_img = None

    if '.dll' in ico_path_lower:
      logger.trace(f'  Skipping "{dir_path}". Folder icon is using a DLL file.')
      return

    if '.exe' in ico_path_lower:
      ico_img = get_exe_icon(os.path.join(dir_path, ico_path), int(ico_index))

    if '.ico' in ico_path_lower:
      ico_img = Image.open(os.path.join(dir_path, ico_path))

    if ico_img and ico_img.mode == 'RGBA':
      r, g, b, a = ico_img.split()
      if not any(a.getdata()):
        ico_img = Image.merge('RGBA', (r, g, b, Image.new('L', ico_img.size, 255)))

    if not ico_img:
      logger.trace(f'  Skipping "{dir_path}". Could not load folder icon.')
      return

    formatted_size = calculate_dir_size(dir_path)
    if formatted_size == '<1 GB' and not OVERLAY_SMALLER_THAN_GB:
      logger.trace(f'  Skipping "{dir_path}". Overlay is disabled for sizes smaller than 1 GB.')
      return

    size_parts = formatted_size.split() if formatted_size else []
    if not (size_parts and len(size_parts) == 2):
      logger.trace(f'  Skipping "{dir_path}". Formatted size is not in format "<value> <unit>".')
      return

    if not os.path.exists(bak_ico_path):
      ico_img.save(bak_ico_path, format='ICO', sizes=[(256, 256)])
      hide_file(bak_ico_path)

    if os.path.exists(new_ico_path):
      show_file(new_ico_path)

    ico_img = ico_img.convert('RGBA')
    img_256 = overlay_file_size_256(size_parts[0], size_parts[1], ico_img)
    img_48 = overlay_file_size_48(size_parts[0], size_parts[1], ico_img)

    other_frames = []
    with Image.open(bak_ico_path) as bak:
      bak_sizes = bak.info.get('sizes', set())
      for size in bak_sizes:
        if size not in {(256, 256), (48, 48)}:
          bak.size = size
          other_frames.append(bak.copy())
      if (16, 16) not in bak_sizes:
        other_frames.append(ico_img.resize((16, 16), Image.LANCZOS))

    img_256.save(new_ico_path, format='ICO', append_images=[img_48] + other_frames)
    logger.success(f'Saved "{new_ico_path}".')

    if DEBUG:
      debug_dir = os.path.join(dir_path, 'icon')
      os.makedirs(debug_dir, exist_ok=True)

      img_256.save(os.path.join(debug_dir, '256.png'), format='PNG')
      img_48.save(os.path.join(debug_dir, '48.png'), format='PNG')

    if ico_path != os.path.basename(bak_ico_path):
      set_folder_icon(dir_path, new_ico_name, override_existing=override)

    hide_file(new_ico_path)

  except Exception as ex:
    logger.error(f'Could not process "{dir_path}": {ex}')

  add_file_attrs(ini_path, HIDDEN_SYSTEM_FILE_ATTRS)

def get_file_size_on_disk(
  file_path: str,
):
  high = ctypes.c_ulong(0)
  low = ctypes.windll.kernel32.GetCompressedFileSizeW(file_path, ctypes.byref(high))
  low_unsigned = low & 0xFFFFFFFF
  if low_unsigned == 0xFFFFFFFF and ctypes.GetLastError() != 0:
    return os.path.getsize(file_path)
  return (high.value << 32) + low_unsigned

def calculate_dir_size(
  dir_path: str,
):
  cache_path = os.path.join(dir_path, DIR_SIZE_FILENAME)
  total_size = None

  if not FORCE_RECALCULATE and os.path.exists(cache_path):
    with open(cache_path, 'r', encoding=PREFERRED_ENCODING) as f:
      lines = f.read().strip().splitlines()
      total_size = int(lines[0].replace(',', '')) if len(lines) > 0 else None
      formatted_size = lines[1] if len(lines) > 1 else None
      if formatted_size and formatted_size != 'None':
        return formatted_size

  if total_size is None:
    total_size = sum(
      get_file_size_on_disk(path)
      for root, _, files in os.walk(dir_path)
      for f in files
      if os.path.exists(path := os.path.join(root, f))
    )
  formatted_size = format_size(total_size)

  cache_contents = f'{total_size}\n{formatted_size or ""}'
  write_hidden_file(cache_path, cache_contents)

  return formatted_size

def overlay_file_size_256(
  value_text: str,
  unit_text: str,
  ico_img: Image.Image,
):
  img = ico_img.resize((SIZE_256, SIZE_256), Image.LANCZOS)

  try:
    value_font = ImageFont.truetype(FONT_NAME, VALUE_FONT_SIZE_256)
    unit_font = ImageFont.truetype(FONT_NAME, UNITS_FONT_SIZE_256)
  except Exception:
    value_font = ImageFont.load_default(VALUE_FONT_SIZE_256)
    unit_font = ImageFont.load_default(UNITS_FONT_SIZE_256)

  draw = ImageDraw.Draw(img)
  bbox_value = draw.textbbox((0, 0), value_text, font=value_font)
  value_w = bbox_value[2] - bbox_value[0]
  value_h = bbox_value[3] - bbox_value[1]

  bbox_unit = draw.textbbox((0, 0), unit_text, font=unit_font)
  unit_w = bbox_unit[2] - bbox_unit[0]
  unit_h = bbox_unit[3] - bbox_unit[1]

  gap = 4
  padding = 8
  box_w = value_w + gap + unit_w + padding * 2
  box_h = value_h + padding * 2
  box_x = SIZE_256 - box_w
  box_y = 0

  box = Image.new('RGBA', (box_w, box_h), (0, 0, 0, 0))
  ImageDraw.Draw(box).rounded_rectangle(
    [0, 0, box_w - 1, box_h - 1],
    radius=padding,
    fill=BG_COLOR,
    corners=(False, False, False, True)
  )
  img.paste(box, (box_x, box_y), box)

  draw = ImageDraw.Draw(img)
  draw.text(
    (box_x + padding - bbox_value[0], box_y + padding - bbox_value[1]),
    value_text,
    font=value_font,
    fill=VALUE_COLOR
  )

  unit_x = box_x + padding + value_w + gap - bbox_unit[0]
  unit_y = box_y + padding + (value_h - unit_h) // 2 - bbox_unit[1]
  draw.text((unit_x, unit_y), unit_text, font=unit_font, fill=UNITS_COLOR)

  return img

def overlay_file_size_48(
  value_text: str,
  unit_text: str,
  ico_img: Image.Image,
):
  img = ico_img.resize((SIZE_48, SIZE_48), Image.LANCZOS)

  try:
    value_font = ImageFont.truetype(FONT_NAME, VALUE_FONT_SIZE_48)
    unit_font = ImageFont.truetype(FONT_NAME, UNITS_FONT_SIZE_48)
  except Exception:
    value_font = ImageFont.load_default(VALUE_FONT_SIZE_48)
    unit_font = ImageFont.load_default(UNITS_FONT_SIZE_48)

  draw = ImageDraw.Draw(img)
  bbox_value = draw.textbbox((0, 0), value_text, font=value_font)
  value_w = bbox_value[2] - bbox_value[0]
  value_h = bbox_value[3] - bbox_value[1]

  bbox_unit = draw.textbbox((0, 0), unit_text, font=unit_font)
  unit_w = bbox_unit[2] - bbox_unit[0]
  unit_h = bbox_unit[3] - bbox_unit[1]

  gap = 2
  padding = 3
  box_h = value_h + padding * 2
  box_x = 0
  box_w = SIZE_48
  box_y = 0

  box = Image.new('RGBA', (box_w, box_h), (0, 0, 0, 0))
  ImageDraw.Draw(box).rectangle([0, 0, box_w - 1, box_h - 1], fill=BG_COLOR)
  img.paste(box, (box_x, box_y), box)

  draw = ImageDraw.Draw(img)
  total_text_w = value_w + gap + unit_w
  text_start_x = (SIZE_48 - total_text_w) // 2
  draw.text(
    (text_start_x - bbox_value[0], box_y + padding - bbox_value[1]),
    value_text,
    font=value_font,
    fill=VALUE_COLOR
  )

  unit_x = text_start_x + value_w + gap - bbox_unit[0]
  unit_y = box_y + padding + (value_h - unit_h) // 2 - bbox_unit[1]
  draw.text(
    (unit_x, unit_y),
    unit_text,
    font=unit_font,
    fill=UNITS_COLOR
  )

  return img

def format_size(
  size_bytes: int,
):
  units = ['GB', 'TB', 'PB']
  size = size_bytes / (1024 * 1024 * 1024)
  if size < 1:
    return f'<1 {units[0]}'
  for unit in units:
    if size < 1024 or unit == units[-1]:
      return f'{math.ceil(int(size * 100) / 100)}  {unit}'
    size /= 1024

def get_exe_icon(
  exe_path: str,
  index: int,
):
  size = MAX_ICO_SIZE
  hicon_large = ctypes.c_void_p()

  hr = ctypes.windll.shell32.SHDefExtractIconW(
    exe_path, index, 0,
    ctypes.byref(hicon_large),
    None,
    size
  )

  if hr != 0 or not hicon_large.value:
    return None

  hicon = hicon_large.value
  screen_dc = win32gui.GetDC(0)

  try:
    hdc = win32ui.CreateDCFromHandle(screen_dc)
    hdc_mem = hdc.CreateCompatibleDC()
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc, size, size)
    hdc_mem.SelectObject(hbmp)
    hdc_mem.FillSolidRect((0, 0, size, size), 0)
    win32gui.DrawIconEx(hdc_mem.GetSafeHdc(), 0, 0, hicon, size, size, 0, None, win32con.DI_NORMAL)
    bmpstr = hbmp.GetBitmapBits(True)
    img = Image.frombuffer('RGBA', (size, size), bmpstr, 'raw', 'BGRA', 0, 1)
  finally:
    win32gui.DestroyIcon(hicon)
    hdc_mem.DeleteDC()
    hdc.DeleteDC()
    win32gui.ReleaseDC(0, screen_dc)

  return img

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

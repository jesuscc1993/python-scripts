import ctypes
import math
import os
import subprocess
import sys
import win32con
import win32gui
import win32ui
import winsound

from PIL import Image, ImageDraw, ImageFont
from mtlogger import logger
from mtprompt import Prompt

from _common import DESKTOP_INI_FILENAME, ICO_FILENAME, MAX_ICO_SIZE, get_ini_icon, read_ini, set_folder_icon

ICO_BAK_FILENAME = 'icon.bak.ico'
DIR_SIZE_FILENAME = 'dir_file_size.txt'

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
  parent_depth = parent_path.rstrip(os.sep).count(os.sep)

  for root, dirs, _ in os.walk(parent_path):
    current_depth = root.rstrip(os.sep).count(os.sep) - parent_depth
    if current_depth >= depth:
      dirs.clear()
      continue

    for dir_name in dirs:
      child_path = os.path.join(root, dir_name)
      process_dir(child_path, override_existing=False)

  winsound.MessageBeep()
  logger.success(f'Finished setting icons for "{parent_path}".', prefix_newline=True)

def process_dir(dir_path: str, override_existing: bool = False):
  try:
    ini_path = os.path.join(dir_path, DESKTOP_INI_FILENAME)
    config, encoding = read_ini(ini_path)

    ico_config = get_ini_icon(config)
    if not ico_config:
      logger.trace(f'Skipping "{dir_path}". No folder icon is set.')
      return

    if ',' in ico_config:
      ico_path, ico_index = ico_config.rsplit(',', 1)
    else:
      ico_path = ico_config
      ico_index = '0'

    new_ico_name = ICO_FILENAME
    new_ico_path = os.path.join(dir_path, new_ico_name)
    bak_ico_path = os.path.join(dir_path, ICO_BAK_FILENAME)
    override = override_existing or new_ico_name not in ico_path
    if ICO_FILENAME in ico_path and os.path.exists(bak_ico_path):
      ico_path = ico_path.replace(ICO_FILENAME, ICO_BAK_FILENAME)

    ico_img = None

    if '.dll' in ico_path.lower():
      logger.trace(f'Skipping "{dir_path}". Folder icon is using a DLL file.')
      return

    if '.exe' in ico_path.lower():
      ico_img = get_exe_icon(os.path.join(dir_path, ico_path), int(ico_index))

    if '.ico' in ico_path.lower():
      ico_img = Image.open(os.path.join(dir_path, ico_path))

    if ico_img and ico_img.mode == 'RGBA':
      r, g, b, a = ico_img.split()
      if not any(a.getdata()):
        ico_img = Image.merge('RGBA', (r, g, b, Image.new('L', ico_img.size, 255)))

    if not os.path.exists(bak_ico_path):
      ico_img.save(bak_ico_path, format='ICO', sizes=[(256, 256)])
      subprocess.run(['attrib', '+h', bak_ico_path], check=True)

    if os.path.exists(new_ico_path):
      subprocess.run(['attrib', '-h', new_ico_path], check=True)

    ico_img = overlay_file_size(dir_path, ico_img)
    ico_img.save(new_ico_path, format='ICO', sizes=[(256, 256), (48, 48), (16, 16)])
    set_folder_icon(dir_path, new_ico_name, override_existing=override)
    subprocess.run(['attrib', '+h', new_ico_path], check=True)

  except Exception as ex:
    logger.error(f'Could not process "{dir_path}": {ex}')

  subprocess.run(['attrib', '+h', '+s', ini_path], check=True)

def calculate_dir_size(dir_path: str) -> int:
  cache_path = os.path.join(dir_path, DIR_SIZE_FILENAME)

  if os.path.exists(cache_path):
    with open(cache_path, 'r') as f:
      return int(f.read().strip())

  total_size = sum(
    os.path.getsize(os.path.join(root, f))
    for root, _, files in os.walk(dir_path)
    for f in files
  )

  with open(cache_path, 'w') as f:
    f.write(str(total_size))

  subprocess.run(['attrib', '+h', cache_path], check=True)

  return total_size

def overlay_file_size(dir_path: str, ico_img: Image.Image) -> Image.Image:
  total_size = calculate_dir_size(dir_path)

  label = format_size(total_size)
  img = ico_img.convert('RGBA').copy()
  width, height = img.size

  try:
    font = ImageFont.truetype('segoeuib.ttf', 40)
  except Exception:
    font = ImageFont.load_default()

  draw = ImageDraw.Draw(img)
  bbox = draw.textbbox((0, 0), label, font=font)
  text_w = bbox[2] - bbox[0]
  text_h = bbox[3] - bbox[1]

  margin = 0
  padding = 8
  box_w = text_w + padding * 2
  box_h = text_h + padding * 2
  box_x = width - margin - box_w
  box_y = margin

  box = Image.new('RGBA', (box_w, box_h), (25, 25, 25, 256))
  img.paste(box, (box_x, box_y), box)

  draw = ImageDraw.Draw(img)
  draw.text((box_x + padding - bbox[0], box_y + padding - bbox[1]), label, font=font, fill=(255, 255, 255, 255))

  return img

def format_size(size_bytes: int) -> str:
  units = ['GB', 'TB', 'PB']
  size = size_bytes / (1024 * 1024 * 1024)
  if size < 1:
    return f'<1 {units[0]}'
  for unit in units:
    if size < 1024 or unit == units[-1]:
      return f'{math.ceil(size)} {unit}'
    size /= 1024

def get_exe_icon(exe_path: str, index: int):
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

  Prompt.enter_to_exit(timeout=True)

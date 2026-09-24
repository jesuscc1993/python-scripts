import os

from PIL import Image, ImageColor

from _constants import IMAGE_EXTENSIONS

def is_image_file(
  filename: str,
):
  return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS

def round_to_even(
  value: float,
):
  return round(value / 2) * 2

def calc_fit_size(
  w: int,
  h: int,
  target_w: int,
  target_h: int,
):
  scale = min(target_w / w, target_h / h)
  return (round(w * scale), round(h * scale))

def center_offset(
  canvas_size: tuple,
  img_size: tuple,
):
  return ((canvas_size[0] - img_size[0]) // 2, (canvas_size[1] - img_size[1]) // 2)

def resize_image_to_fit(
  img: Image.Image,
  w: int,
  h: int,
):
  new_width, new_height = calc_fit_size(img.width, img.height, w, h)
  return img.resize((new_width, new_height), Image.LANCZOS)

def apply_tint(
  img: Image.Image,
  tint: str,
):
  r, g, b, _ = ImageColor.getcolor(tint, 'RGBA')
  tint_layer = Image.new('RGBA', img.size, (r, g, b, 255))
  tint_layer.putalpha(img.getchannel('A'))
  return tint_layer

def tint_to_hex(
  tint: str,
):
  r, g, b, _ = ImageColor.getcolor(tint, 'RGBA')
  return f'#{r:02x}{g:02x}{b:02x}'

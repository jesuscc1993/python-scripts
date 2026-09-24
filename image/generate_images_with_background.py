import argparse
import mtsound
import os
import shutil
import subprocess

from PIL import Image
from mtlogger import logger
from mtprompt import Prompt, to_dir, to_list, to_path

from _common import apply_tint, center_offset, is_image_file, resize_image_to_fit, round_to_even, tint_to_hex
from _constants import MAX_ICO_SIZE

def main():
  args = parse_args()
  has_args = any(value is not None for value in vars(args).values())

  if has_args:
    foreground_folder = to_dir(args.foreground)
    output_folder = to_dir(args.output)
    background_path = to_path(args.background)
    tints = to_list(args.tint) if args.tint else None
    requested_size = int(args.size) if args.size else None
    foreground_scale = args.foreground_scale if args.foreground_scale is not None else 1.0
    background_scale = args.background_scale if args.background_scale is not None else 1.0
  else:
    foreground_folder = Prompt.dir(
      'Enter the path to the folder containing the foreground images you want to add a background to'
    )
    output_folder = Prompt.dir(
      'Enter the path to the output folder'
    )
    background_path = Prompt.path(
      'Enter the path to the background image or a folder of background images'
    )
    tints = Prompt.list(
      'Enter a comma-separated list of tint colors, to apply to the background(s)',
      optional=True
    )
    requested_size = Prompt.int(
      'Enter the size to resize images to',
      optional=True
    )
    foreground_scale = Prompt.float(
      'Enter the foreground scale',
      optional=True
    )
    background_scale = Prompt.float(
      'Enter the background scale',
      optional=True
    )

  generate_images_with_background(
    foreground_folder,
    output_folder,
    background_path,
    tints,
    requested_size,
    foreground_scale,
    background_scale
  )

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--foreground')
  parser.add_argument('-o', '--output')
  parser.add_argument('-b', '--background')
  parser.add_argument('-t', '--tint')
  parser.add_argument('-s', '--size', type=int)
  parser.add_argument('-fs', '--foreground-scale', type=float)
  parser.add_argument('-bs', '--background-scale', type=float)
  return parser.parse_args()

def generate_images_with_background(
  foreground_folder: str,
  output_folder: str,
  background_path: str,
  tints: list = None,
  requested_size: int = None,
  foreground_scale: float = 1.0,
  background_scale: float = 1.0,
):
  background_paths = get_background_paths(background_path)
  foreground_names = [name for name in os.listdir(foreground_folder) if is_image_file(name)]

  if not background_paths:
    logger.error(f'No background images found at "{background_path}".')
    return

  if not foreground_names:
    logger.error(f'No images found in "{foreground_folder}".')
    return

  os.makedirs(output_folder, exist_ok=True)

  tmp_dir = os.path.join(output_folder, '.tmp')
  os.makedirs(tmp_dir, exist_ok=True)
  subprocess.run(['attrib', '+H', tmp_dir], capture_output=True)

  try:
    for background_img_path in background_paths:
      is_background_svg = os.path.splitext(background_img_path)[1].lower() == '.svg'
      background_native_size = None if is_background_svg else Image.open(background_img_path).size
      canvas_size, foreground_size, background_size = get_layout(requested_size, is_background_svg, background_native_size, foreground_scale, background_scale)

      background_img = open_sized_image(background_img_path, tmp_dir, background_size).convert('RGBA')
      background_name, _ = os.path.splitext(os.path.basename(background_img_path))
      background_output_folder = os.path.join(output_folder, background_name)

      for image_name in foreground_names:
        foreground_path = os.path.join(foreground_folder, image_name)
        foreground_img = open_sized_image(foreground_path, tmp_dir, foreground_size).convert('RGBA')

        for tint in (tints or [None]):
          result = compose_image_with_background(foreground_img, background_img, canvas_size, tint)
          tint_output_folder = os.path.join(background_output_folder, tint_to_hex(tint)) if tint else background_output_folder
          os.makedirs(tint_output_folder, exist_ok=True)

          image_base_name, _ = os.path.splitext(image_name)
          output_path = os.path.join(tint_output_folder, f'{image_base_name}.webp')
          result.save(output_path, format='WEBP', lossless=True, alpha_quality=100)
          logger.success(f'Saved "{output_path}".')
  finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

  mtsound.notify()
  logger.log('Finished generating images with background.')

def get_background_paths(
  background_path: str,
):
  if os.path.isdir(background_path):
    return [os.path.join(background_path, name) for name in os.listdir(background_path) if is_image_file(name)]
  return [background_path]

def open_sized_image(
  image_path: str,
  tmp_dir: str,
  size: tuple,
):
  if os.path.splitext(image_path)[1].lower() == '.svg':
    return Image.open(rasterize_svg(image_path, tmp_dir, size))

  img = Image.open(image_path)
  return resize_image_to_fit(img, size[0], size[1])

def rasterize_svg(
  svg_path: str,
  tmp_dir: str,
  size: tuple,
):
  name, _ = os.path.splitext(os.path.basename(svg_path))
  output_path = os.path.join(tmp_dir, f'{name}.png')
  w, h = size

  result = subprocess.run(
    ['magick', '-background', 'none', svg_path, '-resize', f'{w}x{h}', output_path],
    capture_output=True
  )
  if result.returncode != 0:
    raise RuntimeError(result.stderr.decode(errors='replace'))

  return output_path

def get_layout(
  requested_size: int,
  is_background_svg: bool,
  background_native_size: tuple,
  foreground_scale: float,
  background_scale: float,
):
  base_size = requested_size or MAX_ICO_SIZE
  canvas_size = (base_size, base_size) if is_background_svg else background_native_size

  foreground_size = (round_to_even(canvas_size[0] * foreground_scale), round_to_even(canvas_size[1] * foreground_scale))
  background_size = (round_to_even(canvas_size[0] * background_scale), round_to_even(canvas_size[1] * background_scale))

  return canvas_size, foreground_size, background_size

def compose_image_with_background(
  foreground_img: Image.Image,
  background_img: Image.Image,
  canvas_size: tuple,
  tint: str = None,
):
  canvas_w, canvas_h = canvas_size

  background = background_img
  if tint:
    background = apply_tint(background, tint)

  canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
  canvas.alpha_composite(background, dest=center_offset(canvas.size, background.size))
  canvas.alpha_composite(foreground_img, dest=center_offset(canvas.size, foreground_img.size))

  return canvas

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout = True)
import json
import numpy as np
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont
from mutagen.asf import ASF, ASFByteArrayAttribute
from mutagen.mp4 import MP4, MP4Cover
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm

MUTAGEN_EXTS = {'.mp4', '.m4v', '.mov', '.wmv'}
OTHER_VIDEO_EXTS = {'.mkv', '.avi'}
COMBINED_VIDEO_EXTS = MUTAGEN_EXTS | OTHER_VIDEO_EXTS

SCREENSHOT_SECS = 3 * 60

FONT_NAME = 'segoeuib.ttf'
FONT_SIZE = 24

OVERLAY_PADDING = 4
OVERLAY_LINE_GAP = 8
OVERLAY_BG_ALPHA = 192

def main():
  if len(sys.argv) > 1:
    input_path = sys.argv[1]
  else:
    input_path = Prompt.dir(
      'Enter the path to the directory containing the videos you want to process'
    )

  process_directory(input_path)

def process_directory(
  dir_path: str,
):
  mutagen_files = []
  ffmpeg_files = []

  for f in os.listdir(dir_path):
    ext = get_ext(f)
    if ext in MUTAGEN_EXTS:
      mutagen_files.append(os.path.join(dir_path, f))
    elif ext in OTHER_VIDEO_EXTS:
      ffmpeg_files.append(os.path.join(dir_path, f))

  video_files = mutagen_files + ffmpeg_files

  if not video_files:
    tqdm.write('No video files found.')
    return

  logger.debug('Generating video covers...')

  tmp_dir = os.path.join(dir_path, '.tmp')
  os.makedirs(tmp_dir, exist_ok = True)
  subprocess.run(['attrib', '+H', tmp_dir], capture_output = True)

  try:
    for file_path in tqdm(video_files, unit = 'file'):
      process_file(file_path, tmp_dir)
  finally:
    shutil.rmtree(tmp_dir, ignore_errors = True)
    logger.success('Finished generating video covers.')

def get_ext(
  file_path: str,
):
  return os.path.splitext(file_path)[1].lower()

def process_file(
  file_path: str,
  tmp_dir: str,
):
  name = os.path.basename(file_path)
  stem = os.path.splitext(name)[0]
  ext = get_ext(file_path)

  probe = get_video_info(file_path)
  if probe is None:
    tqdm.write(f'Could not read video info for: {name}')
    return

  duration_secs = float(probe['format'].get('duration', 0))
  file_size = int(probe['format'].get('size', os.path.getsize(file_path)))

  seek_secs = min(SCREENSHOT_SECS, duration_secs * 0.25)

  frame_path = os.path.join(tmp_dir, stem + '.jpg')
  out_path = os.path.join(tmp_dir, stem + ext)

  try:
    capture_frame(file_path, seek_secs, frame_path)
    img = Image.open(frame_path).convert('RGB')
    img = crop_black_borders(img)
    img = crop_to_16_9(img)
    img.thumbnail((256, 256), Image.LANCZOS)
    img = draw_stats_overlay(img, duration_secs, file_size)
    img.save(frame_path, 'JPEG', quality = 90)

    if ext in MUTAGEN_EXTS:
      embed_cover_mutagen(file_path, frame_path)
    else:
      embed_cover_ffmpeg(file_path, frame_path, out_path, ext)
      os.replace(out_path, file_path)

    tqdm.write(f'  Embedded cover into: {name}')
  except Exception as ex:
    tqdm.write(f'  Failed: {ex}')

def embed_cover_mutagen(
  file_path: str,
  cover_path: str,
):
  with open(cover_path, 'rb') as f:
    data = f.read()
  ext = get_ext(file_path)
  if ext == '.wmv':
    tags = ASF(file_path)
    tags['WM/Picture'] = [ASFByteArrayAttribute(data)]
    tags.save()
  else:
    tags = MP4(file_path)
    tags['covr'] = [MP4Cover(data, MP4Cover.FORMAT_JPEG)]
    tags.save()


def embed_cover_ffmpeg(
  file_path: str,
  cover_path: str,
  output_path: str,
  ext: str,
):
  if ext == '.mkv':
    cmd = [
      'ffmpeg', '-y',
      '-loglevel', 'error',
      '-i', file_path,
      '-attach', cover_path,
      '-metadata:s:t:0', 'mimetype=image/jpeg',
      '-metadata:s:t:0', 'filename=cover.jpg',
      '-c', 'copy',
      output_path
    ]
  else:
    cmd = [
      'ffmpeg', '-y',
      '-loglevel', 'error',
      '-i', file_path,
      '-i', cover_path,
      '-map', '0',
      '-map', '1',
      '-c', 'copy',
      '-disposition:v:1', 'attached_pic',
      output_path
    ]

  result = subprocess.run(cmd, capture_output = True)
  if result.returncode != 0:
    raise RuntimeError(result.stderr.decode(errors = 'replace'))

def get_video_info(
  file_path: str,
):
  try:
    result = subprocess.run(
      [
        'ffprobe', '-v', 'quiet',
        '-analyzeduration', '0', '-probesize', '5000000',
        '-print_format', 'json',
        '-show_format',
        file_path
      ],
      capture_output = True,
      text = True
    )
    return json.loads(result.stdout)
  except Exception:
    return None

def crop_to_16_9(
  img: Image.Image,
):
  w, h = img.size
  if w / h > 16 / 9:
    new_w = int(h * 16 / 9)
    x = (w - new_w) // 2
    img = img.crop((x, 0, x + new_w, h))
  return img

def crop_black_borders(
  img: Image.Image,
  threshold=10,
):
  arr = np.array(img)
  mask = arr.max(axis=2) > threshold
  rows = np.any(mask, axis=1)
  cols = np.any(mask, axis=0)
  if not rows.any() or not cols.any():
    return img
  y0, y1 = np.where(rows)[0][[0, -1]]
  x0, x1 = np.where(cols)[0][[0, -1]]
  return img.crop((x0, y0, x1 + 1, y1 + 1))

def capture_frame(
  file_path: str,
  seek_secs: float,
  output_path: str,
):
  subprocess.run(
    [
      'ffmpeg', '-y',
      '-loglevel', 'error',
      '-analyzeduration', '0', '-probesize', '5000000',
      '-ss', str(seek_secs),
      '-i', file_path,
      '-vframes', '1',
      '-q:v', '2',
      output_path
    ],
    stdout = subprocess.DEVNULL,
    stderr = subprocess.DEVNULL
  )
  if not os.path.exists(output_path):
    raise RuntimeError(f'Failed to extract frame from: {os.path.basename(file_path)}')

def format_duration(
  secs: float,
):
  secs = int(secs)
  h = secs // 3600
  m = (secs % 3600) // 60
  s = secs % 60
  if h > 0:
    return f'{h}:{m:02d}:{s:02d}'
  return f'{m}:{s:02d}'

def format_size(
  size_bytes: int,
):
  if size_bytes >= 1024 ** 3:
    return f'{round(size_bytes / (1024 ** 3), 2)} GB'
  return f'{round(size_bytes / (1024 ** 2))} MB'

def draw_stats_overlay(
  img: Image.Image,
  duration_secs: float,
  file_size: int,
):
  draw = ImageDraw.Draw(img, 'RGBA')

  try:
    font = ImageFont.truetype(FONT_NAME, FONT_SIZE)
  except Exception:
    font = ImageFont.load_default()

  img_w, img_h = img.size

  draw_label(draw, font, format_duration(duration_secs), side = 'left', img_w = img_w)
  draw_label(draw, font, format_size(file_size), side = 'right', img_w = img_w)

  return img.convert('RGB')


def draw_label(
  draw: ImageDraw.ImageDraw,
  font: ImageFont.FreeTypeFont,
  text: str,
  side: str,
  img_w: int,
):
  bb = draw.textbbox((0, 0), text, font=font)
  tw = bb[2] - bb[0]
  th = bb[3] - bb[1]
  top = bb[1]

  box_w = tw + OVERLAY_PADDING * 2
  box_h = th + OVERLAY_PADDING * 2

  box_x = 0 if side == 'left' else img_w - box_w
  box_x2 = box_w if side == 'left' else img_w

  draw.rectangle([box_x, 0, box_x2, box_h], fill = (0, 0, 0, OVERLAY_BG_ALPHA))

  tx = box_x + OVERLAY_PADDING
  draw.text((tx, OVERLAY_PADDING - top), text, font = font, fill = (255, 255, 255, 255))

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)

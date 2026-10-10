import json
import os
import shutil
import subprocess
import sys

from mtlogger import logger
from mtprompt import Prompt, to_path
from mutagen.asf import ASF
from mutagen.mp4 import MP4
from tqdm import tqdm

from _common import generate_tmp_dir, get_ext
from _constants import MP4_EXTS, VIDEO_EXTS, WMV_EXT


def main():
  if len(sys.argv) > 1:
    input_path = to_path(sys.argv[1])
  else:
    input_path = Prompt.path('Enter the path to a video file or directory')

  logger.log(f'Removing video covers from "{input_path}"...')
  logger.hr()

  try:
    if os.path.isfile(input_path):
      tmp_dir = generate_tmp_dir(os.path.dirname(input_path))
      process_file(input_path, tmp_dir)
    else:
      tmp_dir = generate_tmp_dir(input_path)
      process_directory(input_path, tmp_dir)

  finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

  logger.hr()
  logger.log(f'Finished removing video covers from "{input_path}".')


def process_directory(
  dir_path: str,
  tmp_dir: str,
):
  video_files = []

  for root, dirs, file_names in os.walk(dir_path):
    if os.path.abspath(root) == os.path.abspath(tmp_dir):
      dirs[:] = []
      continue

    for file_name in file_names:
      if get_ext(file_name) in VIDEO_EXTS:
        video_files.append(os.path.join(root, file_name))

  if not video_files:
    tqdm.write('No video files found.')
    return

  for file_path in tqdm(video_files, unit='file'):
    process_file(file_path, tmp_dir)


def process_file(
  file_path: str,
  tmp_dir: str,
):
  ext = get_ext(file_path)
  if ext not in VIDEO_EXTS:
    return False

  if ext == WMV_EXT:
    return remove_asf_cover(file_path)
  if ext in MP4_EXTS:
    return remove_mp4_cover(file_path)

  return remove_ffmpeg_covers(file_path, tmp_dir)


def remove_mp4_cover(
  file_path: str,
):
  media = MP4(file_path)
  if media.tags is None or 'covr' not in media.tags:
    logger.log(f'No embedded cover found in "{os.path.basename(file_path)}".')
    return False

  del media['covr']
  media.save()
  logger.success(
    f'Removed embedded cover from "{os.path.basename(file_path)}".'
  )
  return True


def remove_asf_cover(
  file_path: str,
):
  media = ASF(file_path)
  if 'WM/Picture' not in media:
    logger.log(f'No embedded cover found in "{os.path.basename(file_path)}".')
    return False

  del media['WM/Picture']
  media.save()
  logger.success(
    f'Removed embedded cover from "{os.path.basename(file_path)}".'
  )
  return True


def find_cover_streams(
  file_path: str,
) -> list[int]:
  result = subprocess.run(
    [
      'ffprobe',
      '-v',
      'quiet',
      '-analyzeduration',
      '0',
      '-probesize',
      '5000000',
      '-print_format',
      'json',
      '-show_streams',
      file_path,
    ],
    check=False,
    capture_output=True,
    encoding='utf-8',
    errors='replace',
    text=True,
  )
  if result.returncode != 0:
    raise RuntimeError(
      result.stderr.strip() or f'Could not inspect "{file_path}".'
    )

  streams = json.loads(result.stdout).get('streams', [])
  cover_indices = []
  for stream in streams:
    stream_type = stream.get('codec_type')
    filename = stream.get('tags', {}).get('filename', '').casefold()
    is_attached_picture = stream_type == 'video' and stream.get(
      'disposition', {}
    ).get('attached_pic')
    is_cover_attachment = (
      stream_type == 'attachment' and filename == 'cover.jpg'
    )
    is_cover_video = stream_type == 'video' and filename == 'cover.jpg'
    if is_attached_picture or is_cover_attachment or is_cover_video:
      cover_indices.append(stream['index'])

  return cover_indices


def remove_ffmpeg_covers(
  file_path: str,
  tmp_dir: str,
):
  cover_indices = find_cover_streams(file_path)
  if not cover_indices:
    logger.log(f'No embedded cover found in "{os.path.basename(file_path)}".')
    return False

  output_path = os.path.join(tmp_dir, os.path.basename(file_path))
  cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', file_path, '-map', '0']
  for stream_index in cover_indices:
    cmd.extend(['-map', f'-0:{stream_index}'])
  cmd.extend(['-c', 'copy', output_path])

  result = subprocess.run(cmd, check=False, capture_output=True)
  if (
    result.returncode != 0
    or not os.path.isfile(output_path)
    or os.path.getsize(output_path) == 0
  ):
    if os.path.exists(output_path):
      os.remove(output_path)
    error_message = (
      result.stderr.decode(errors='replace').strip()
      or 'ffmpeg did not create a non-empty output file.'
    )
    logger.warn(
      f'Failed to remove cover from "{os.path.basename(file_path)}": {error_message}'
    )
    return False

  os.replace(output_path, file_path)
  logger.success(
    f'Removed embedded cover from "{os.path.basename(file_path)}".'
  )
  return True


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

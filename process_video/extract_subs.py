import json
import os
import re
import subprocess
import sys

from mtlogger import logger
from mtprompt import Prompt
from mtvalidation import to_path

from _common import post_process_subs_file
from _constants import SUBTITLE_EXTS_BY_CODEC, VIDEO_EXTS
from _settings import SETTINGS

LANGUAGE = 'eng'
SUBTITLES_PATH = 'subtitles'


def main():
  if len(sys.argv) > 1:
    input_path = to_path(sys.argv[1])
  else:
    input_path = Prompt.path('Enter the path to a video file or directory')

  logger.log(f'Extracting subs for "{input_path}"...')
  logger.hr()

  if os.path.isfile(input_path):
    process_file(input_path)
  else:
    process_directory(input_path)

  logger.hr()
  logger.log(f'Finished extracting subs for "{input_path}".')


def process_file(
  file_path: str,
):
  file_name = os.path.basename(file_path)
  name, ext = os.path.splitext(file_name)
  if ext.lower() not in VIDEO_EXTS:
    return

  subtitle_streams = find_subtitle_streams(file_path, LANGUAGE.lower())
  if not subtitle_streams:
    logger.warn(f'Skipping "{file_name}". No {LANGUAGE} subtitles found.\n')
    return

  dir_path = os.path.dirname(file_path)
  in_place_output_path = dir_path
  in_folder_output_path = os.path.join(dir_path, SUBTITLES_PATH)

  if SETTINGS['extract_to_folder']:
    output_path = in_folder_output_path
    os.makedirs(output_path, exist_ok=True)
  else:
    output_path = in_place_output_path

  track_titles = [
    sanitize_track_title(title or '') if len(subtitle_streams) > 1 else ''
    for _, _, title in subtitle_streams
  ]
  title_counts = {
    title: track_titles.count(title) for title in set(track_titles) if title
  }

  for track_number, ((stream_idx, codec_name, _), track_title) in enumerate(
    zip(subtitle_streams, track_titles), start=1
  ):
    subtitle_ext = SUBTITLE_EXTS_BY_CODEC[codec_name]
    if track_title:
      duplicate_suffix = (
        f'_{track_number}' if title_counts[track_title] > 1 else ''
      )
      track_suffix = f' - {track_title}{duplicate_suffix}'
    else:
      track_suffix = '' if track_number == 1 else f'_{track_number}'
    subtitles_file_name = f'{name}{track_suffix}{subtitle_ext}'
    if any(
      os.path.exists(os.path.join(path, subtitles_file_name))
      for path in [in_place_output_path, in_folder_output_path]
    ):
      logger.trace(
        f'Skipping "{subtitles_file_name}". Subtitles file already exists.\n'
      )
      continue

    dest_file_path = os.path.join(output_path, subtitles_file_name)
    extract_subtitles(
      file_path, dest_file_path, file_name, stream_idx, subtitle_ext
    )

  if os.path.isdir(output_path) and not os.listdir(output_path):
    os.rmdir(output_path)


def sanitize_track_title(title: str) -> str:
  title = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', ' ', title)
  return re.sub(r'\s+', ' ', title).strip(' .')


def process_directory(
  dir_path: str,
):
  for root, dirs, file_names in os.walk(dir_path):
    dirs[:] = [dir_name for dir_name in dirs if dir_name.casefold() != '.tmp']
    for file_name in file_names:
      process_file(os.path.join(root, file_name))


def extract_subtitles(
  src_file_path: str,
  dest_file_path: str,
  file_name: str,
  stream_idx: str,
  subtitle_ext: str,
):
  no_subs_found_message = (
    f'Skipping "{file_name}". No {LANGUAGE} subtitles found.\n'
  )

  logger.log(f'Extracting {LANGUAGE} subtitles for "{file_name}"...')
  cmd = [
    'ffmpeg',
    '-y',
    '-analyzeduration',
    '0',
    '-probesize',
    '5000000',
    '-i',
    src_file_path,
    '-map',
    f'0:{stream_idx}',
    '-c:s',
    'copy',
    dest_file_path,
  ]
  subprocess.run(
    cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
  )

  if os.path.exists(dest_file_path):
    if os.path.getsize(dest_file_path) == 0:
      os.remove(dest_file_path)
      logger.warn(no_subs_found_message)
    else:
      post_process_subs_file(dest_file_path, subtitle_ext)
      logger.success(f'Extracted "{dest_file_path}".\n')
  else:
    logger.warn(no_subs_found_message)


def find_subtitle_streams(
  src_file_path: str, target_language: str
) -> list[tuple[int, str, str | None]]:
  try:
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
        src_file_path,
      ],
      check=False,
      capture_output=True,
      encoding='utf-8',
      errors='replace',
      text=True,
    )
    matching_streams = []
    for stream in json.loads(result.stdout).get('streams', []):
      if (
        stream.get('codec_type') == 'subtitle'
        and stream.get('codec_name') in SUBTITLE_EXTS_BY_CODEC
      ):
        tags = stream.get('tags', {})
        language = tags.get('language', '').lower()
        if language.startswith(target_language):
          matching_streams.append(
            (stream['index'], stream['codec_name'], tags.get('title'))
          )
    return matching_streams

  except Exception:
    logger.failure(f'Failed to find subtitle stream for "{src_file_path}".')
  return []


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

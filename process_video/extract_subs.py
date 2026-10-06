import json
import os
import subprocess
import sys

from mtlogger import logger
from mtprompt import Prompt, to_path

from _common import post_process_subs_file
from _constants import SUBTITLE_EXTS_BY_CODEC, VIDEO_EXTS
from _settings import SETTINGS

LANGUAGE = 'eng'
SUBTITLES_PATH = 'subtitles'

def main():
  if len(sys.argv) > 1:
    input_path = to_path(sys.argv[1])
  else:
    input_path = Prompt.path(
      'Enter the path to a video file or directory'
    )

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

  stream_idx, codec_name = find_subtitle_stream(file_path, LANGUAGE.lower())
  if stream_idx is None:
    logger.warn(f'Skipping "{file_name}". No {LANGUAGE} subtitles found.\n')
    return

  subtitle_ext = SUBTITLE_EXTS_BY_CODEC[codec_name]
  subtitles_file_name = name + subtitle_ext

  dir_path = os.path.dirname(file_path)
  in_place_output_path = dir_path
  in_folder_output_path = os.path.join(dir_path, SUBTITLES_PATH)

  if any(os.path.exists(os.path.join(path, subtitles_file_name)) for path in [in_place_output_path, in_folder_output_path]):
    logger.trace(f'Skipping "{file_name}". Subtitles file already exists.\n')
    return

  if SETTINGS['extract_to_folder']:
    output_path = in_folder_output_path
    os.makedirs(output_path, exist_ok = True)
  else:
    output_path = in_place_output_path

  dest_file_path = os.path.join(output_path, subtitles_file_name)
  extract_subtitles(file_path, dest_file_path, file_name, stream_idx, subtitle_ext)

  if os.path.isdir(output_path) and not os.listdir(output_path):
    os.rmdir(output_path)

def process_directory(
  dir_path: str,
):
  for root, _, file_names in os.walk(dir_path):
    for file_name in file_names:
      process_file(os.path.join(root, file_name))

def extract_subtitles(
  src_file_path: str,
  dest_file_path: str,
  file_name: str,
  stream_idx: str,
  subtitle_ext: str,
):
  no_subs_found_message = f'Skipping "{file_name}". No {LANGUAGE} subtitles found.\n'

  logger.log(f'Extracting {LANGUAGE} subtitles for "{file_name}"...')
  cmd = [
    'ffmpeg',
    '-y',
    '-analyzeduration', '0',
    '-probesize', '5000000',
    '-i', src_file_path,
    '-map', f'0:{stream_idx}',
    '-c:s', 'copy',
    dest_file_path
  ]
  subprocess.run(cmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

  if os.path.exists(dest_file_path):
    if os.path.getsize(dest_file_path) == 0:
      os.remove(dest_file_path)
      logger.warn(no_subs_found_message)
    else:
      post_process_subs_file(dest_file_path, subtitle_ext)
      logger.success(f'Extracted "{dest_file_path}".\n')
  else:
    logger.warn(no_subs_found_message)

def find_subtitle_stream(src_file_path: str, target_language: str) -> tuple[str | None, str | None]:
  try:
    result = subprocess.run(
      [
        'ffprobe',
        '-v', 'quiet',
        '-analyzeduration', '0',
        '-probesize', '5000000',
        '-print_format', 'json',
        '-show_streams',
        src_file_path
      ],
      capture_output = True,
      text = True,
      timeout = 5
    )
    for stream in json.loads(result.stdout).get('streams', []):
      if stream.get('codec_type') == 'subtitle' and stream.get('codec_name') in SUBTITLE_EXTS_BY_CODEC:
        tags = stream.get('tags', {})
        language = tags.get('language', '').lower()
        if language.startswith(target_language):
          return stream['index'], stream.get('codec_name')

  except Exception:
    logger.failure(f'Failed to find subtitle stream for "{src_file_path}".')
  return None, None

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

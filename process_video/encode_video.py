import json
import os
import shutil
import subprocess
import sys

from mtlogger import logger
from mtprompt import Prompt, to_bool
from mtvalidation import to_path
from send2trash import send2trash
from tqdm import tqdm

from _common import generate_tmp_dir, get_ext
from _constants import MKV_EXT, VIDEO_EXTS, VIDEO_EXTS_WITH_HEVC_SUPPORT

SETTINGS = {
  'attachment_codec': 'copy',
  'audio_codec': 'copy',
  'bitrate': '0',
  'data_codec': 'copy',
  'max_interleave_delta': '0',
  'preset': 'p6',
  'quality': '28',
  'rate_control': 'vbr',
  'subtitle_codec': 'copy',
  'tune': 'hq',
  'video_codec': 'hevc_nvenc',
}


def main():
  if len(sys.argv) > 1:
    input_path = to_path(sys.argv[1])
    backup_files = to_bool(sys.argv[2]) if len(sys.argv) > 2 else False
  else:
    input_path = Prompt.path('Enter the path to a video file or directory')
    backup_files = Prompt.bool('Backup original files?', default=False)

  logger.hr()
  logger.log(f'Encoding videos in "{input_path}"...\n')

  tmp_dir = None

  try:
    if os.path.isfile(input_path):
      tmp_dir = generate_tmp_dir(os.path.dirname(input_path))
      process_file(input_path, tmp_dir, backup_files)
    else:
      tmp_dir = generate_tmp_dir(input_path)
      process_directory(input_path, tmp_dir, backup_files)

  finally:
    if tmp_dir:
      shutil.rmtree(tmp_dir, ignore_errors=True)

  logger.log(f'\nFinished encoding videos in "{input_path}".')
  logger.hr()


def process_directory(input_path: str, tmp_dir: str, backup_files: bool):
  files = [
    os.path.join(root, filename)
    for root, _, filenames in os.walk(input_path)
    for filename in filenames
    if should_process_item(os.path.join(root, filename))
  ]

  with tqdm(total=len(files), desc='Processing files', unit='file') as progress:
    for file_path in files:
      file_name = os.path.basename(file_path)
      progress.set_postfix_str(file_name)

      try:
        process_file(file_path, tmp_dir, backup_files)
      except Exception as ex:
        tqdm.write(logger.format_error(f'Failed to encode "{file_name}": {ex}'))

      progress.update(1)
      tqdm.write(logger.format_trace(f'Finished encoding "{file_name}".'))


def process_file(input_path: str, tmp_dir: str, backup_files: bool):
  file_name, file_ext = os.path.splitext(os.path.basename(input_path))
  parent_dir = os.path.dirname(input_path)
  backup_file_path = os.path.join(parent_dir, f'{file_name}.bak{file_ext}')

  output_ext = (
    file_ext if file_ext.lower() in VIDEO_EXTS_WITH_HEVC_SUPPORT else MKV_EXT
  )
  output_file_path = os.path.join(parent_dir, f'{file_name}{output_ext}')
  if os.path.normcase(output_file_path) != os.path.normcase(
    input_path
  ) and os.path.exists(output_file_path):
    raise FileExistsError(f'Output file already exists: "{output_file_path}"')

  tmp_file_path = os.path.join(tmp_dir, f'{file_name}{output_ext}')

  command = [
    'ffmpeg',
    '-i',
    input_path,
    *get_map_args(input_path),
    '-c:v',
    SETTINGS['video_codec'],
    '-preset',
    SETTINGS['preset'],
    '-tune',
    SETTINGS['tune'],
    '-rc',
    SETTINGS['rate_control'],
    '-cq',
    SETTINGS['quality'],
    '-b:v',
    SETTINGS['bitrate'],
    '-c:a',
    SETTINGS['audio_codec'],
    '-c:s',
    SETTINGS['subtitle_codec'],
    '-c:d',
    SETTINGS['data_codec'],
    '-c:t',
    SETTINGS['attachment_codec'],
    '-max_interleave_delta',
    SETTINGS['max_interleave_delta'],
    '-loglevel',
    'error',
    tmp_file_path,
  ]

  subprocess.run(command, check=True)

  if not os.path.isfile(tmp_file_path) or os.path.getsize(tmp_file_path) == 0:
    raise RuntimeError(f'Invalid output file: "{tmp_file_path}"')

  if backup_files:
    if os.path.exists(backup_file_path) and Prompt.bool(
      f'A backup already exists for file "{file_name}": Keep older backup?',
      default=True,
    ):
      os.remove(input_path)
    else:
      os.replace(input_path, backup_file_path)
  else:
    send2trash(input_path)

  shutil.move(tmp_file_path, output_file_path)


def get_map_args(input_path: str):
  result = subprocess.run(
    [
      'ffprobe',
      '-v',
      'error',
      '-select_streams',
      'v',
      '-show_entries',
      'stream=index:stream_disposition=attached_pic',
      '-of',
      'json',
      input_path,
    ],
    capture_output=True,
    text=True,
    check=True,
  )

  streams = json.loads(result.stdout).get('streams', [])

  return [
    '-map',
    '0',
    *[
      arg
      for stream in streams
      if stream.get('disposition', {}).get('attached_pic', 0)
      for arg in ('-map', f'-0:{stream["index"]}')
    ],
  ]


def should_process_item(item_path: str):
  file_name = os.path.basename(item_path).lower()

  return (
    os.path.isfile(item_path)
    and get_ext(file_name) in VIDEO_EXTS
    and '.bak.' not in file_name
  )


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

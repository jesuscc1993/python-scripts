import os
import shutil
import subprocess
import sys

from mtlogger import logger
from mtprompt import Prompt, to_bool
from mtvalidation import to_path

from _common import generate_tmp_dir

SETTINGS = {
  'attachment_codec': 'copy',
  'audio_codec': 'copy',
  'bitrate': '0',
  'data_codec': 'copy',
  'ffmpeg': 'ffmpeg',
  'map': '0',
  'max_interleave_delta': '0',
  'preset': 'p6',
  'quality': '28',
  'rate_control': 'vbr',
  'subtitle_codec': 'copy',
  'tune': 'hq',
  'video_codec': 'hevc_nvenc',
  'video_ext': '.mkv',
}


def main():
  if len(sys.argv) > 1:
    input_path = to_path(sys.argv[1])
    backup_files = to_bool(sys.argv[2]) if len(sys.argv) > 2 else False
  else:
    input_path = Prompt.path('Enter the path to a video file or directory')
    backup_files = Prompt.bool('Backup original files?', default=False)

  logger.log(f'Encoding videos in "{input_path}"...')
  logger.hr()

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

  logger.hr()
  logger.log(f'Finished encoding videos in "{input_path}".')


def process_directory(input_path: str, tmp_dir: str, backup_files: bool):
  files = [
    os.path.join(input_path, filename)
    for filename in os.listdir(input_path)
    if should_process_item(os.path.join(input_path, filename))
  ]

  for file_path in files:
    process_file(file_path, tmp_dir, backup_files)


def process_file(input_path: str, tmp_dir: str, backup_files: bool):
  file_name, file_ext = os.path.splitext(os.path.basename(input_path))
  backup_path = os.path.join(
    os.path.dirname(input_path), f'{file_name}.bak{file_ext}'
  )
  output_path = os.path.join(tmp_dir, os.path.basename(input_path))

  command = [
    SETTINGS['ffmpeg'],
    '-i',
    input_path,
    '-map',
    SETTINGS['map'],
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
    '-stats',
    output_path,
  ]

  logger.log(f'Processing "{input_path}"...')
  subprocess.run(command, check=True)

  if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
    raise RuntimeError(f'Invalid output file: "{output_path}"')

  if backup_files and (
    not os.path.exists(backup_path)
    or not Prompt.bool(
      f'A backup already exists for file "{file_name}": Keep older backup?',
      default=True,
    )
  ):
    os.replace(input_path, backup_path)
  else:
    os.remove(input_path)

  shutil.move(output_path, input_path)
  logger.log()


def should_process_item(item_path: str):
  filename = os.path.basename(item_path).lower()

  return (
    os.path.isfile(item_path)
    and filename.endswith(SETTINGS['video_ext'])
    and '.bak.' not in filename
  )


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

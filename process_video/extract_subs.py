import os
import subprocess
import sys

from _common import prompt_path, strip_tags_from_subs_file
from mtlogger import logger

LANGUAGE = 'eng'
SUBTITLES_PATH = 'subtitles'
SUBTITLE_EXT = '.srt'
VIDEO_EXTS = ['.mp4', '.mkv']

def main():
  if len(sys.argv) > 1:
    input_path = sys.argv[1]
  else:
    input_path = prompt_path('Enter the path to a video file or directory:\n')

  if os.path.isfile(input_path):
    process_file(input_path)
  else:
    process_directory(input_path)

def process_file(file_path):
  file_name = os.path.basename(file_path)
  name, ext = os.path.splitext(file_name)
  if ext.lower() not in VIDEO_EXTS:
    return

  dir_path = os.path.dirname(file_path)
  output_path = os.path.join(dir_path, SUBTITLES_PATH)
  os.makedirs(output_path, exist_ok = True)

  dest_file_path = os.path.join(output_path, name + SUBTITLE_EXT)
  extract_subtitles(file_path, dest_file_path, file_name)

def process_directory(dir_path):
  for file_name in os.listdir(dir_path):
    process_file(os.path.join(dir_path, file_name))

def extract_subtitles(src_file_path, dest_file_path, file_name):
  cmd = [
    'ffmpeg',
    '-i', src_file_path,
    '-map', f'0:s:m:language:{LANGUAGE}:0?',
    '-c:s', 'srt',
    dest_file_path
  ]
  subprocess.run(cmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

  if os.path.exists(dest_file_path):
    if os.path.getsize(dest_file_path) == 0:
      os.remove(dest_file_path)
      logger.warn(f' No {LANGUAGE} subtitles found for "{file_name}". Removed empty subtitle file.')
    else:
      strip_tags_from_subs_file(dest_file_path)
      logger.log(f'Extracted {LANGUAGE} subtitles for "{file_name}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

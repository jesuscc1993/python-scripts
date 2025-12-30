
import os
import sys
import subprocess

from mtlogger import logger

AUDIO_EXTS = [
  '.aac',
  '.aiff',
  '.alac',
  '.flac',
  '.m4a',
  '.ogg',
  '.opus',
  '.wav',
  '.wma',
]
MP3_BITRATE = '320k'
MP3_EXT = '.mp3'

def main():
  parent_path = sys.argv[1] if len(sys.argv) > 1 else prompt_path('Enter the folder path to process:\n')
  bitrate = sys.argv[2] if len(sys.argv) > 2 else MP3_BITRATE

  for root, _, filenames in os.walk(parent_path):
    for og_filename in filenames:
      ext = os.path.splitext(og_filename)[1].lower()
      if ext in AUDIO_EXTS:
        new_filename = os.path.splitext(og_filename)[0] + MP3_EXT
        input_path = os.path.join(root, og_filename)
        output_path = os.path.join(root, new_filename)
        try:
          convert_to_mp3(input_path, output_path, bitrate)
          os.remove(input_path)
          logger.log(f'Converted "{og_filename}" to "{new_filename}".')
        except Exception as ex:
          logger.error(f'Failed to convert "{input_path}": {ex}')

def convert_to_mp3(input_path, output_path, bitrate):
  result = subprocess.run(
    [
      'ffmpeg',
      '-i', input_path,
      '-b:a', bitrate,
      '-codec:a', 'libmp3lame',
      '-map', 'a',
      '-y',
      output_path
    ],
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE
  )
  if result.returncode != 0:
    raise RuntimeError(result.stderr.decode('utf-8'))

def prompt_path(prompt_message, optional = False):
  path = input(prompt_message).strip(' "\'')
  if not path or not os.path.isdir(path):
    logger.error(f'The specified path "{path}" is not a directory.')
    if not optional: sys.exit(1)
    return None
  logger.log()
  return path

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

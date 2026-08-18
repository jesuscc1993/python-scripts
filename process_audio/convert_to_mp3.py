
import os
import sys
import subprocess

from send2trash import send2trash

from concurrent.futures import ThreadPoolExecutor, as_completed
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm

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
  parent_path = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the folder path to process')
  bitrate = sys.argv[2] if len(sys.argv) > 2 else MP3_BITRATE

  files_to_convert = []
  for root, _, filenames in os.walk(parent_path):
    for og_filename in filenames:
      ext = os.path.splitext(og_filename)[1].lower()
      if ext in AUDIO_EXTS:
        new_filename = os.path.splitext(og_filename)[0] + MP3_EXT

        files_to_convert.append((
          os.path.join(root, og_filename),
          os.path.join(root, new_filename),
          og_filename,
          new_filename
        ))

  with ThreadPoolExecutor() as executor:
    futures = [
      executor.submit(
        worker,
        input_path,
        output_path,
        input_filename,
        output_filename,
        bitrate
      )
      for input_path, output_path, input_filename, output_filename in files_to_convert
    ]
    for _ in tqdm(as_completed(futures), total = len(futures), desc = "Converting files to MP3"):
      pass

  tqdm.write("Finished converting files to MP3.")

def worker(
  input_file_path: str,
  output_file_path: str,
  input_filename: str,
  output_filename: str,
  bitrate: str,
):
  try:
    convert_to_mp3(input_file_path, output_file_path, bitrate)
    send2trash(input_file_path)
    tqdm.write(f'Converted "{input_filename}" to "{output_filename}".')
  except Exception as ex:
    tqdm.write(f'Failed to convert "{input_file_path}":\n{ex}')

def convert_to_mp3(
  input_file_path: str,
  output_file_path: str,
  bitrate: str,
):
  result = subprocess.run(
    [
      'ffmpeg',
      '-i', input_file_path,
      '-b:a', bitrate,
      '-codec:a', 'libmp3lame',
      '-map', 'a',
      '-y',
      output_file_path
    ],
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE
  )
  if result.returncode != 0:
    raise RuntimeError(result.stderr.decode('utf-8'))

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

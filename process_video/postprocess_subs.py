import os
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import add_missing_spaces, prompt_path, strip_tags_from_subs_file

SUBTITLE_EXT = '.srt'

def main():
  if len(sys.argv) > 1:
    input_path = sys.argv[1]
  else:
    input_path = prompt_path('Enter the path to an SRT file or directory:\n')

  if os.path.isfile(input_path):
    process_file(input_path)
  else:
    process_directory(input_path)

def process_file(file_path):
  file_name = os.path.basename(file_path)
  ext = os.path.splitext(file_name)[1].lower()
  if ext != SUBTITLE_EXT:
    return

  dest_file_path = file_path
  strip_tags_from_subs_file(dest_file_path)
  add_missing_spaces(dest_file_path)
  logger.log(f'Fixed subtitles for "{file_name}".')

def process_directory(dir_path):
  for file_name in os.listdir(dir_path):
    process_file(os.path.join(dir_path, file_name))

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enterToExit()

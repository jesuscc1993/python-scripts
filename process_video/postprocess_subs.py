import os
import sys

from mtlogger import logger
from mtprompt import Prompt, to_path

from _common import add_missing_spaces, strip_tags_from_subs_file

SUBTITLE_EXT = '.srt'

def main():
  if len(sys.argv) > 1:
    input_path = to_path(sys.argv[1])
  else:
    input_path = Prompt.path(
      'Enter the path to an SRT file or directory'
    )

  if os.path.isfile(input_path):
    process_file(input_path)
  else:
    process_directory(input_path)

def process_file(
  file_path: str,
):
  file_name = os.path.basename(file_path)
  ext = os.path.splitext(file_name)[1].lower()
  if ext != SUBTITLE_EXT:
    return

  dest_file_path = file_path
  strip_tags_from_subs_file(dest_file_path)
  add_missing_spaces(dest_file_path)
  logger.log(f'Fixed subtitles for "{file_name}".')

def process_directory(
  dir_path: str,
):
  for root, _, file_names in os.walk(dir_path):
    for file_name in file_names:
      process_file(os.path.join(root, file_name))

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

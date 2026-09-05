import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import compress_folder, ZIP_TYPES

def main():
  folder_path = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the folder you want to compress')
  output_type = sys.argv[2] if len(sys.argv) > 2 else ZIP_TYPES[0]
  delete_original = sys.argv[3].lower() == 'y' if len(sys.argv) > 3 else False

  compress_folder(folder_path, output_type, delete_original)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

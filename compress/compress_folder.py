import sys

from mtlogger import logger
from mtprompt import Prompt, to_bool, to_dir, to_list

from _common import compress_folder, ZIP_TYPES

def main():
  folder_path = to_dir(sys.argv[1]) if len(sys.argv) > 1 else Prompt.dir('Enter the path to the folder you want to compress')
  output_type = sys.argv[2] if len(sys.argv) > 2 else ZIP_TYPES[0]
  delete_original = to_bool(sys.argv[3]) if len(sys.argv) > 3 else False
  exclusion_patterns = to_list(sys.argv[4]) if len(sys.argv) > 4 else None

  logger.log(f'Compressing folder "{folder_path}"...')
  compress_folder(folder_path, output_type, delete_original, exclusion_patterns)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

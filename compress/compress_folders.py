import sys

from mtlogger import logger
from mtprompt import Prompt, to_bool, to_dir, to_int, to_list

from _common import compress_child_folders, ZIP_TYPES

def main():
  parent_dir = to_dir(sys.argv[1]) if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the folders you want to compress')
  output_type = sys.argv[2] if len(sys.argv) > 2 else ZIP_TYPES[0]
  delete_original = to_bool(sys.argv[3]) if len(sys.argv) > 3 else False
  exclusion_patterns = to_list(sys.argv[4]) if len(sys.argv) > 4 else None
  min_depth = to_int(sys.argv[5]) if len(sys.argv) > 5 else 1
  max_depth = to_int(sys.argv[6]) if len(sys.argv) > 6 else min_depth

  logger.log(f'Compressing folders in "{parent_dir}"...')
  compress_child_folders(parent_dir, output_type, delete_original, exclusion_patterns, min_depth, max_depth)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

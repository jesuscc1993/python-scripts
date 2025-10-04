import os
import sys

from mtlogger import logger

def main():
  if len(sys.argv) > 2:
    dest_path = sys.argv[1]
    src_path = sys.argv[2]
  else:
    dest_path = prompt_path('Delete from path:\n')
    src_path = prompt_path('...files that exist on path:\n')

  compare_paths_and_delete_files(src_path, dest_path)
  delete_empty_folders(dest_path)

def compare_paths_and_delete_files(src_path, dest_path):
  for root, _, files in os.walk(src_path):
    for f in files:
      path_a = os.path.join(root, f)
      path_b = path_a.replace(src_path, dest_path, 1)
      if os.path.exists(path_b):
        os.remove(path_b)
        logger.debug(f'Deleted "{path_b}".')
  logger.log(f'Finished deleting from "{dest_path}" the files that already existed in "{src_path}".\n')

def delete_empty_folders(parent_folder):
  for root, dirs, _ in os.walk(parent_folder, topdown = False):
    for dir_name in dirs:
      try:
        os.rmdir(os.path.join(root, dir_name))
      except OSError:
        pass

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

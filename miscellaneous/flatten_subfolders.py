import os
import shutil
import sys

from mtlogger import logger
from mtprompt import Prompt

PREPEND_PARENT = True

def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing the folders you want to flatten'
    )

  flatten_subfolders(parent_dir)

def flatten_subfolders(parent_dir: str):
  logger.log(f'Flattening subfolders in "{parent_dir}"...')

  for root, dirs, _ in os.walk(parent_dir):
    for dir_name in dirs:
      dir_path = os.path.join(root, dir_name)
      for sub_root, _, sub_files in os.walk(dir_path, topdown=False):
        for file_name in sub_files:
          src_path = os.path.join(sub_root, file_name)
          if PREPEND_PARENT:
            parent_name = os.path.basename(sub_root)
            dest_path = os.path.join(root, f'{parent_name} - {file_name}')
          else:
            dest_path = os.path.join(root, file_name)

          if os.path.exists(dest_path):
            logger.warn(f'Skipping "{src_path}". "{dest_path}" already exists.')
            continue

          shutil.move(src_path, dest_path)

        if os.listdir(sub_root):
          logger.warn(f'Not deleting "{sub_root}" because it is not empty.')
        else:
          os.rmdir(sub_root)

  logger.success(f'Finished flattening subfolders in "{parent_dir}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

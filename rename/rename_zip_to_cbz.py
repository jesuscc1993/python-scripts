import os
import sys
import winsound

from mtlogger import logger
from mtprompt import Prompt

def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your ZIP files'
    )

  rename_zip_to_cbz(parent_dir)

def rename_zip_to_cbz(parent_dir: str):
  logger.log(f'Renaming ZIP files to CBZ in "{parent_dir}"...')

  for root, _, files in os.walk(parent_dir):
    for name in files:
      old_path = os.path.join(root, name)
      new_path = os.path.splitext(old_path)[0] + '.cbz'

      if not name.lower().endswith('.zip') or not os.path.isfile(old_path):
        continue

      os.rename(old_path, new_path)
      logger.debug(f'Renamed "{old_path}" to "{new_path}".')

  logger.success(f'Renamed ZIP files to CBZ in "{parent_dir}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  winsound.MessageBeep()
  Prompt.enter_to_exit()

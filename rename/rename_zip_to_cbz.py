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

  with os.scandir(parent_dir) as items:
    for item in items:
      if item.is_file() and item.name.lower().endswith('.zip'):
        new_path = os.path.splitext(item.path)[0] + '.cbz'
        os.rename(item.path, new_path)
        logger.debug(f'Renamed "{item.name}" to "{os.path.basename(new_path)}".')
    logger.success(f'Renamed ZIP files to CBZ in "{parent_dir}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  winsound.MessageBeep()
  Prompt.enter_to_exit()

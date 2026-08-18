import os
import shutil
import sys

from mtlogger import logger
from mtprompt import Prompt

def main():
  if len(sys.argv) > 1:
    src_path = sys.argv[1]
  else:
    src_path = Prompt.dir(
      'Enter the directory containing .bak files to restore'
    )

  restore_backups(src_path)

def restore_backups(
  dir_path: str,
):
	for filename in os.listdir(dir_path):
		if '.bak.' in filename:
			bak_path = os.path.join(dir_path, filename)
			og_name = filename.replace('.bak.', '.', 1)
			og_path = os.path.join(dir_path, og_name)

			shutil.copy2(bak_path, og_path)
			logger.log(f'Restored "{bak_path}" as "{og_path}".')
	logger.success(f'Finished restoring .bak files in "{dir_path}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

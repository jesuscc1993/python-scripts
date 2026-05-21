import os
import shutil
import sys

from mtlogger import logger
from mtprompt import Prompt

from _common import prompt_path

def main():
  if len(sys.argv) > 1:
    src_path = sys.argv[1]
  else:
    src_path = prompt_path('Enter the directory containing .bak files to restore:\n')

  restore_backups(src_path)
  logger.log(f'\nFinished restoring .bak files in "{src_path}".\n')
  main()

def restore_backups(dir_path):
	for filename in os.listdir(dir_path):
		if '.bak.' in filename:
			bak_path = os.path.join(dir_path, filename)
			og_name = filename.replace('.bak.', '.', 1)
			og_path = os.path.join(dir_path, og_name)

			shutil.copy2(bak_path, og_path)
			logger.log(f'Restored "{bak_path}" as "{og_path}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
    Prompt.enterToExit()

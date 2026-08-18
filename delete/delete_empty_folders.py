import os

from mtlogger import logger
from mtprompt import Prompt

def main():
  parent_folder = Prompt.dir(
    'Enter the path to the parent directory containing the folders or images'
  )

  delete_empty_folders(parent_folder)

def delete_empty_folders(
  parent_folder_path: str,
):
  none_deleted = True

  for root, dirs, _ in os.walk(parent_folder_path, topdown = False):
    for dir_name in dirs:
      dir_path = os.path.join(root, dir_name)
      try:
        os.rmdir(dir_path)
        none_deleted = False
        logger.log(f'Deleted empty folder: "{dir_path}"')
      except OSError:
        pass

  if none_deleted:
    logger.log('No empty folders were found.')
  else:
    logger.success('Finished deleting empty folders.')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

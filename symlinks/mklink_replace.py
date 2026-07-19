

import os
from os import path

from _common import run_as_admin

from mtlogger import logger
from mtprompt import Prompt

def main():
  logger.debug('Script will backup and replace files containing "link token" with symlinks to files containing "target token".\nOnly target token can be an empty string.\nExample: link token = "_4k", target token = "" will create a "movie_4k.bk" link pointing to "movie.bk".\n')
  parent_dir = Prompt.dir('Enter the parent dir')
  link_token = Prompt.str('Enter the link token')
  target_token = Prompt.str('Enter the target token', default='')

  for dir_path, dir_names, file_names in os.walk(parent_dir):
    if 'backup' in dir_path:
      continue

    items_to_process = [f for f in file_names if link_token in f]
    if not items_to_process:
      continue

    backup_dir = os.path.join(dir_path, 'backup')
    if not path.exists(backup_dir):
      os.makedirs(backup_dir)

    for item_name in items_to_process:
      item_path = os.path.join(dir_path, item_name)
      os.rename(item_path, os.path.join(backup_dir, item_name))

      target_name = item_name.replace(link_token, target_token)
      target_path = os.path.join(dir_path, target_name)

      link_path = item_path
      os.symlink(target_path, link_path)
      logger.info(f'Created symlink: {path.relpath(link_path, parent_dir)} -> {path.relpath(target_path, parent_dir)}')

if __name__ == '__main__':
  try:
    run_as_admin()
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

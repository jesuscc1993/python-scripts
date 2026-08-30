import json
import os

from dotenv import load_dotenv
from mtlogger import logger
from mtprompt import Prompt

from _common import link_dir, link_file, run_as_admin

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SPECIFIC_GAME_SAVES_PATH = os.getenv('SPECIFIC_GAME_SAVES_PATH')

def main():
  logger.log(f'Generating links for specific game saves...')

  script_dir = os.path.dirname(os.path.abspath(__file__))
  mappings_path = os.path.join(script_dir, 'specific_game_save_mappings.json')

  if not os.path.exists(mappings_path):
    logger.error(f'File not found: "{mappings_path}". Check readme for instructions.')
    return
  with open(mappings_path, 'r', encoding='utf-8') as file:
    groups = json.load(file)

  for group in groups:
    path_prefix = group.get('path_prefix')
    items = group.get('items')
    logger.log(f'\nProcessing group: {path_prefix} with {len(items)} mappings.')

    for item in items:
      src = item.get('src')
      dest = item.get('dest')
      is_file = item.get('isFile', False)
      expand = item.get('expand', True)

      if not dest:
        dest = os.path.basename(src)
        # logger.debug(f'  No destination specified for source "{src}". Defaulting to: "{dest}".')

      src_path = os.path.join(path_prefix, src)
      dest_path = os.path.join(SPECIFIC_GAME_SAVES_PATH, dest)

      if not src_path or not dest_path:
        logger.warn(f'Invalid mapping entry: {item}. Skipping...')
        continue

      if is_file:
        link_file(src_path, dest_path, make_dirs=expand)
      else:
        link_dir(src_path, dest_path, make_dirs=expand)

  logger.success('Finished generating links for specific game saves.')

if __name__ == '__main__':
  try:
    run_as_admin()
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

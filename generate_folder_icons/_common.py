import os
import sys

from PIL import Image
from mtlogger import logger

from _sound_utils import play_notification_sound

DESKTOP_INI_FILENAME = 'desktop.ini'
ICON_FILENAME = 'icon.ico'
MAX_ICON_SIZE = 256
DEFAULT_ICON_SIZES = [16, 256]

def prompt_path(prompt_message, optional = False):
  path = input(prompt_message).strip(' "\'')
  if not path or not os.path.isdir(path):
    logger.error(f'The specified path "{path}" is not a directory.')
    if not optional: sys.exit(1)
    return None
  logger.log()
  return path

def prompt_depth():
  try:
    depth = int(input('Enter the depth for processing subfolders (default: 1):\n').strip() or 1)
    if depth < 0:
      raise ValueError()
    return depth
  except ValueError:
    logger.error('\nDepth must be a positive integer.')
    return

def process_parent_folder(parent_folder, depth, image_filenames):
  process_folder(parent_folder, image_filenames)

  parent_folder = os.path.abspath(parent_folder)
  parent_depth = parent_folder.rstrip(os.sep).count(os.sep)

  for root, dirs, _ in os.walk(parent_folder):
    current_depth = root.rstrip(os.sep).count(os.sep) - parent_depth
    if current_depth >= depth:
      dirs.clear()
      continue

    for dir_name in dirs:
      item_path = os.path.join(root, dir_name)
      process_folder(item_path, image_filenames)

  play_notification_sound()
  logger.log(f'\nFinished setting icons for "{parent_folder}".')

def process_folder(folder_path, image_filenames):
  image_path = None
  for image_filename in image_filenames:
    potential_path = os.path.join(folder_path, image_filename)
    if os.path.exists(potential_path):
      image_path = potential_path
      break

  if image_path:
    ico_path = os.path.join(folder_path, ICON_FILENAME)
    image_to_ico(image_path, ico_path)
    set_folder_icon(folder_path)
  else:
    logger.debug(f'No suitable image found in "{folder_path}"')

def image_to_ico(image_path, icon_path, icon_sizes = DEFAULT_ICON_SIZES):
  try:
    if os.path.exists(icon_path):
      os.unlink(icon_path)

    with Image.open(image_path) as img:
      if img.width < MAX_ICON_SIZE:
        img = img.resize((MAX_ICON_SIZE, int(MAX_ICON_SIZE * img.height / img.width)), resample = Image.LANCZOS)
      img.thumbnail((MAX_ICON_SIZE, MAX_ICON_SIZE), Image.LANCZOS)
      background = Image.new('RGBA', (MAX_ICON_SIZE, MAX_ICON_SIZE), (0, 0, 0, 0))
      offset = (int((MAX_ICON_SIZE - img.size[0]) / 2), int((MAX_ICON_SIZE - img.size[1]) / 2))
      background.paste(img, offset)
      background.save(icon_path, format = 'ICO', sizes = [(s, s) for s in icon_sizes])
  except Exception as ex:
    logger.error(f'Error converting "{image_path}" to ICO: {ex}')

def set_folder_icon(folder_path):
  try:
    desktop_ini_path = os.path.join(folder_path, DESKTOP_INI_FILENAME)
    icon_path = os.path.join(folder_path, ICON_FILENAME)

    if os.path.exists(desktop_ini_path):
      os.system(f'attrib -h -s "{desktop_ini_path}"')

    with open(desktop_ini_path, 'w') as desktop_ini:
      desktop_ini.write('[.ShellClassInfo]\n')
      desktop_ini.write(f'IconResource={ICON_FILENAME},0\n')

    os.system(f'attrib +h +s "{desktop_ini_path}"')
    os.system(f'attrib +h "{icon_path}"')
    os.system(f'attrib +s "{folder_path}"')

    logger.log(f'Saved "{icon_path}" and "{desktop_ini_path}".')
  except PermissionError:
    logger.warn(f' Permission denied: "{desktop_ini_path}". You may need to run the script as an administrator.')
  except Exception as ex:
    logger.error(f'Error setting folder icon to "{folder_path}": {ex}')

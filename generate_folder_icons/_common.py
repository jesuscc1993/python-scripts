import os
import winsound

from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from mtlogger import logger
from tqdm import tqdm

DESKTOP_INI_FILENAME = 'desktop.ini'
ICON_FILENAME = 'icon.ico'
MAX_ICON_SIZE = 256
DEFAULT_ICON_SIZES = [16, 256]

def process_parent_folder(parent_folder, depth, image_filenames):
  parent_folder = os.path.abspath(parent_folder)
  parent_depth = parent_folder.rstrip(os.sep).count(os.sep)

  folders_to_process = [parent_folder]
  for root, dirs, _ in os.walk(parent_folder):
    current_depth = root.rstrip(os.sep).count(os.sep) - parent_depth
    if current_depth >= depth:
      dirs.clear()
      continue

    for dir_name in dirs:
      folders_to_process.append(os.path.join(root, dir_name))

  with ThreadPoolExecutor() as executor, tqdm(total = len(folders_to_process), desc = f'Processing "{parent_folder}"') as progress:
    for _ in executor.map(lambda f: process_folder(f, image_filenames), folders_to_process):
      progress.update(1)

  winsound.MessageBeep()
  logger.log(f'\nFinished setting icons for "{parent_folder}".')

def process_folder(folder_path, image_filenames):
  image_path = None
  ico_path = os.path.join(folder_path, ICON_FILENAME)
  ico_exists = os.path.exists(ico_path)

  skipped = False
  for image_filename in image_filenames:
    potential_path = os.path.join(folder_path, image_filename)
    if os.path.exists(potential_path):
      if not ico_exists or is_file_newer_than(potential_path, ico_path):
        image_path = potential_path
      else:
        skipped = True
      break

  if image_path:
    image_to_ico(image_path, ico_path)
    set_folder_icon(folder_path)
  elif skipped:
    tqdm.write(logger.formatWarn(f'No image found in "{folder_path}" is newer than the icon.'))
  else:
    tqdm.write(logger.formatWarn(f'No suitable image found in "{folder_path}".'))

def is_file_newer_than(file_a, file_b):
  return os.path.getmtime(file_a) > os.path.getmtime(file_b)

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
    logger.error(f'Error converting "{image_path}" to ICO:\n{ex}')

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

    # parent_dir = os.path.dirname(folder_path)
    # tqdm.write(logger.formatDebug(f'Saved "{os.path.relpath(icon_path, parent_dir)}" and "{os.path.relpath(desktop_ini_path, parent_dir)}".'))
  except PermissionError:
    tqdm.write(logger.formatWarn(f'Permission denied: "{desktop_ini_path}". You may need to run the script as an administrator.'))
  except Exception as ex:
    tqdm.write(logger.formatError(f'Error setting folder icon to "{folder_path}":\n{ex}'))

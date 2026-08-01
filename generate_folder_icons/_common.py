import os
import subprocess
import winsound

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from mtlogger import logger
from tqdm import tqdm

MAX_ICO_SIZE = 256
DEFAULT_ICO_SIZES = [16, 48, 256]
ICO_FILENAME = 'icon.ico'

DESKTOP_INI_FILENAME = 'desktop.ini'
INI_PREFERRED_ENCODING = 'utf-8'
INI_FALLBACK_ENCODING = 'cp1252'
INI_ICON_KEY = 'IconResource'
INI_SHELL_SECTION = '.ShellClassInfo'

def process_parent_folder(parent_folder: str, depth: int, image_filenames: list[str]):
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

def process_folder(folder_path: str, image_filenames: list[str]):
  image_path = None
  ico_path = os.path.join(folder_path, ICO_FILENAME)
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
    set_folder_icon(folder_path, ICO_FILENAME)
  elif skipped:
    tqdm.write(logger.formatWarn(f'No image found in "{folder_path}" is newer than the icon.'))
  else:
    tqdm.write(logger.formatWarn(f'No suitable image found in "{folder_path}".'))

def is_file_newer_than(file_a: str, file_b: str):
  return os.path.getmtime(file_a) > os.path.getmtime(file_b)

def image_to_ico(image_path: str, ico_path: str, icon_sizes: list[int] = DEFAULT_ICO_SIZES):
  try:
    if os.path.exists(ico_path):
      os.unlink(ico_path)

    with Image.open(image_path) as img:
      if img.width < MAX_ICO_SIZE:
        img = img.resize((MAX_ICO_SIZE, int(MAX_ICO_SIZE * img.height / img.width)), resample = Image.LANCZOS)
      img.thumbnail((MAX_ICO_SIZE, MAX_ICO_SIZE), Image.LANCZOS)
      background = Image.new('RGBA', (MAX_ICO_SIZE, MAX_ICO_SIZE), (0, 0, 0, 0))
      offset = (int((MAX_ICO_SIZE - img.size[0]) / 2), int((MAX_ICO_SIZE - img.size[1]) / 2))
      background.paste(img, offset)
      background.save(ico_path, format = 'ICO', sizes = [(s, s) for s in icon_sizes])

  except Exception as ex:
    logger.error(f'Error converting "{image_path}" to ICO:\n{ex}')

def set_folder_icon(folder_path: str, ico_path: str, override_existing: bool = False):
  try:
    desktop_ini_path = os.path.join(folder_path, DESKTOP_INI_FILENAME)

    if os.path.exists(desktop_ini_path):
      show_file(desktop_ini_path)

    config, encoding = read_ini(desktop_ini_path)

    if get_ini_icon(config) and not override_existing:
      logger.trace(f'Skipping "{folder_path}". A folder icon is already set.')
      return

    set_ini_icon(config, ico_path)
    write_ini(desktop_ini_path, encoding, config)
    hide_file(desktop_ini_path)

  except PermissionError:
    tqdm.write(logger.formatWarn(f'Permission denied: "{desktop_ini_path}". You may need to run the script as an administrator.'))

  except Exception as ex:
    tqdm.write(logger.formatError(f'Error setting folder icon to "{folder_path}":\n{ex}'))

def read_ini(ini_path: str, encoding: str = INI_PREFERRED_ENCODING):
  config = ConfigParser()
  config.optionxform = str

  try:
    if os.path.exists(ini_path):
      config.read(ini_path, encoding=encoding)

  except Exception as ex:
    try:
      encoding = INI_FALLBACK_ENCODING
      config.read(ini_path, encoding=encoding)

    except Exception as ex:
      logger.error(f'Failed to read "{ini_path}": {ex}')

  return config, encoding

def write_ini(ini_path: str, encoding: str, config: ConfigParser):
  if os.path.exists(ini_path):
    remove_file_attrs(ini_path, ['h', 's'])

  with open(ini_path, 'w', encoding=encoding) as ini:
    config.write(ini)
    logger.success(f'Saved "{ini_path}".')

  add_file_attrs(ini_path, ['h', 's'])

def get_ini_icon(config: ConfigParser):
  return config.get(INI_SHELL_SECTION, INI_ICON_KEY, fallback=None)

def set_ini_icon(config: ConfigParser, ico_path: str, ico_index: int = 0):
  if INI_SHELL_SECTION not in config:
    config[INI_SHELL_SECTION] = {}

  config[INI_SHELL_SECTION][INI_ICON_KEY] = f'{ico_path},{ico_index}'

def add_file_attrs(file_path: str, attrs: list[str]):
  if os.path.exists(file_path):
    subprocess.run(['attrib'] + ['+' + attr for attr in attrs] + [file_path], check=True)

def remove_file_attrs(file_path: str, attrs: list[str]):
  if os.path.exists(file_path):
    subprocess.run(['attrib'] + ['-' + attr for attr in attrs] + [file_path], check=True)

def hide_file(file_path: str):
  add_file_attrs(file_path, ['h'])

def show_file(file_path: str):
  remove_file_attrs(file_path, ['h'])

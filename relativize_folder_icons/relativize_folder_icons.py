import configparser
import ctypes
import os

from mtlogger import logger
from mtprompt import Prompt

def main():
  parent_folder = Prompt.dir(
    'Enter the path to the directory containing the folders you want to process'
  )
  recursive = Prompt.bool(
    'Run recursively in subfolders?',
    default = False
  )
  process_subfolders(parent_folder, recursive, is_root = True)

def process_subfolders(base_path, recursive, is_root = False):
  logger.log(f'Processing "{base_path}"...')

  for root, dirs, files in os.walk(base_path):
    if is_root and 'desktop.ini' in files:
      process_folder(root)

    if recursive or is_root:
      for dir in dirs:
        subfolder_path = os.path.join(root, dir)
        process_subfolders(subfolder_path, recursive)

  logger.success(f'Finished processing "{base_path}".')

def process_folder(folder_path):
  desktop_ini_path = os.path.join(folder_path, 'desktop.ini')
  if not os.path.isfile(desktop_ini_path):
    return

  config = configparser.ConfigParser()
  config.optionxform = str

  try:
    ctypes.windll.kernel32.SetFileAttributesW(desktop_ini_path, 0x80)
    config.read(desktop_ini_path)

    if '.ShellClassInfo' in config and 'IconResource' in config['.ShellClassInfo']:
      icon_resource = config['.ShellClassInfo']['IconResource']
      if icon_resource.endswith(',0'):
        icon_resource = icon_resource[:-2]

      if os.path.isabs(icon_resource) and folder_path in icon_resource:
        relative_icon_path = os.path.relpath(icon_resource, folder_path)
        config['.ShellClassInfo']['IconResource'] = relative_icon_path

        with open(desktop_ini_path, 'w') as desktop_ini:
          config.write(desktop_ini)
        logger.success(f'Updated folder "{folder_path}" with IconResource "{relative_icon_path}".')
      else:
        logger.trace(f'Skipping folder "{folder_path}" with IconResource "{icon_resource}".')

      ctypes.windll.kernel32.SetFileAttributesW(desktop_ini_path, 0x02 | 0x04)
  except PermissionError:
    logger.error(f'Permission denied for "{desktop_ini_path}"')
  except Exception as ex:
    logger.error(f'Could not process "{desktop_ini_path}":\n{ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enter_to_exit()

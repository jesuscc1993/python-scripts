import ctypes
import json
import os
import sys
import winreg

from mtlogger import logger
from mtprompt import Prompt

from _registry import add_registry_entry, delete_registry_entry, get_registry_value

ASSOCIATIONS_JSON = './associations.json'
FILE_EXTS = 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts'

def run_as_admin():
  if os.name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

def main():
  run_as_admin()

  associations = get_associations()
  root_icons_path = associations.get('icons_path')

  for mapping in associations.get('mappings'):
    shell = mapping.get('shell')
    type_name = mapping.get('type_name')
    fallback_icon = mapping.get('fallback_icon')
    icons_path = mapping.get('icons_path') or root_icons_path

    for type_mapping in mapping.get('types'):
      if isinstance(type_mapping, str):
        ext = type_mapping
        class_name = type_mapping
      else:
        ext = type_mapping.get('ext')
        class_name = type_mapping.get('class')

      ext_icon_path = get_icon_path(icons_path, ext) or get_icon_path(icons_path, class_name)
      fallback_icon_path = get_icon_path(icons_path, fallback_icon)
      file_type = get_registry_value(winreg.HKEY_CLASSES_ROOT, f'.{ext}', '') or f'{class_name.lower()}file'

      delete_registry_entry(winreg.HKEY_CURRENT_USER, f'{FILE_EXTS}\\.{ext}\\UserChoice')
      add_registry_entry(winreg.HKEY_CLASSES_ROOT, f'.{ext}', '', file_type)

      if type_name:
        add_registry_entry(winreg.HKEY_CLASSES_ROOT, file_type, 'FriendlyTypeName', type_name)

      type_icon = ext_icon_path or fallback_icon_path
      if type_icon and os.path.exists(type_icon):
        add_registry_entry(winreg.HKEY_CLASSES_ROOT, f'{file_type}\\DefaultIcon', '', f'"{type_icon}"')

      if shell:
        for item in shell:
          command = item.get('command')
          icon = item.get('icon')
          key = item.get('key')
          label = item.get('label')

          shell_key = f'{file_type}\\shell\\{key}'

          add_registry_entry(winreg.HKEY_CLASSES_ROOT, shell_key, '', label or '')

          if icon:
            add_registry_entry(winreg.HKEY_CLASSES_ROOT, shell_key, 'Icon', icon)
          else:
            delete_registry_entry(winreg.HKEY_CLASSES_ROOT, shell_key, 'Icon')

          add_registry_entry(winreg.HKEY_CLASSES_ROOT, f'{shell_key}\\command', '', command)

      logger.log(f'Saved registry key "HKEY_CLASSES_ROOT\\{file_type}" for extension "HKEY_CLASSES_ROOT\\.{ext}".\n')

  logger.success('Saved registry entries.')

def get_associations():
  with open(ASSOCIATIONS_JSON, 'r') as associations:
    return json.load(associations)

def get_icon_path(
  icons_path: str,
  name: str,
):
  if name == None:
    return None

  path = os.path.join(icons_path, f'{name.upper()}.ico')
  return path if os.path.exists(path) else None

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

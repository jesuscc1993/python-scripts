import ctypes
import json
import os
import winreg

from mtlogger import logger

from _registry import add_registry_entry, delete_registry_entry, get_registry_value

ASSOCIATIONS_JSON = './associations.json'
FILE_EXTS = 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts'

def main():
  if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    logger.error('Admin privileges required. Please run as administrator.')
    return

  associations = get_associations()
  root_icons_path = associations.get('icons_path')

  for mapping in associations.get('mappings'):
    shell = mapping.get('shell')
    type_name = mapping.get('type_name')
    fallback_icon = mapping.get('fallback_icon')
    icons_path = mapping.get('icons_path') or root_icons_path

    for type in mapping.get('types'):
      if isinstance(type, str):
        ext = type
        ext_icon = type
      else:
        ext = type.get('ext')
        ext_icon = type.get('parent')

      ext_icon_path = get_icon_path(icons_path, ext_icon.upper())
      fallback_icon_path = get_icon_path(icons_path, fallback_icon)
      file_type = get_registry_value(winreg.HKEY_CLASSES_ROOT, f'.{ext}', '') or f'{ext.lower()}file'

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

  logger.log('Registry entries saved successfully.')

def get_associations():
  with open(ASSOCIATIONS_JSON, 'r') as associations:
    return json.load(associations)

def get_icon_path(icons_path, name):
  path = os.path.join(icons_path, f'{name}.ico')
  return path if os.path.exists(path) else None

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('\nPress Enter to exit...')

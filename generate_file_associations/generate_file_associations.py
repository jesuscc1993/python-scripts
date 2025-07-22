import ctypes
import json
import os
import winreg

ASSOCIATIONS_JSON = './associations.json'
FILE_EXTS = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts'

def main():
  if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    print('Admin privileges required. Please run as administrator.')
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
      file_type = get_registry_value(f'.{ext}', '') or f'{ext.lower()}file'

      delete_registry_entry(f'{FILE_EXTS}\\.{ext}\\UserChoice')
      add_registry_entry(f'.{ext}', '', file_type)

      if type_name:
        add_registry_entry(f'{file_type}', 'FriendlyTypeName', type_name)

      type_icon = ext_icon_path or fallback_icon_path
      if type_icon and os.path.exists(type_icon):
        add_registry_entry(f'{file_type}\\DefaultIcon', '', f'"{type_icon}"')

      if shell:
        for item in shell:
          add_registry_entry(f'{file_type}\\shell\\{item["key"]}\\command', '', item['command'])

      print(f'Saved registry key "HKEY_CLASSES_ROOT\\{file_type}" for extension "HKEY_CLASSES_ROOT\\.{ext}".')

  print('Registry entries saved successfully.')

def get_associations():
  with open(ASSOCIATIONS_JSON, 'r') as associations:
    return json.load(associations)

def get_registry_value(path, name):
  try:
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, path) as key:
      return winreg.QueryValueEx(key, name)[0]
  except FileNotFoundError:
    return None
  except Exception as ex:
    print(f'Error reading registry entry for {path}: {ex}')
    return None

def delete_registry_entry(path):
  try:
    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, path)
  except FileNotFoundError:
    pass
  except Exception as ex:
    print(f'Error deleting registry entry for {path}: {ex}')

def add_registry_entry(path, name, value):
  try:
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, path) as key:
      winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
  except Exception as ex:
    print(f'Error adding registry entry for {path}: {ex}')

def get_icon_path(icons_path, name):
  path = os.path.join(icons_path, f'{name}.ico')
  return path if os.path.exists(path) else None

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('\nPress Enter to exit...')

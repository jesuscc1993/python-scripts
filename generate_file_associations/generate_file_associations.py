import ctypes
import json
import os
import winreg

ASSOCIATIONS_JSON = './associations.json'
FILE_EXTS = 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts'
HKEY_NAMES = {
  winreg.HKEY_CLASSES_ROOT: 'HKEY_CLASSES_ROOT',
  winreg.HKEY_CURRENT_CONFIG: 'HKEY_CURRENT_CONFIG',
  winreg.HKEY_CURRENT_USER: 'HKEY_CURRENT_USER',
  winreg.HKEY_LOCAL_MACHINE: 'HKEY_LOCAL_MACHINE',
  winreg.HKEY_USERS: 'HKEY_USERS',
}

def main():
  if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    print('[ERROR] Admin privileges required. Please run as administrator.')
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
        add_registry_entry(winreg.HKEY_CLASSES_ROOT, f'{file_type}', 'FriendlyTypeName', type_name)

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

      print(f'[LOG] Saved registry key "HKEY_CLASSES_ROOT\\{file_type}" for extension "HKEY_CLASSES_ROOT\\.{ext}".\n')

  print('[LOG] Registry entries saved successfully.')

def get_associations():
  with open(ASSOCIATIONS_JSON, 'r') as associations:
    return json.load(associations)

def get_registry_value(root, path, name):
  try:
    with winreg.OpenKey(root, path) as key:
      return winreg.QueryValueEx(key, name)[0]
  except FileNotFoundError:
    return None
  except Exception as ex:
    print(f'[ERROR] Could not get value for registry entry "{get_registry_key(root, path, name)}": {ex}')
    return None

def delete_registry_entry(root, path, name = None):
  try:
    if not name:
      winreg.DeleteKey(root, path)
      print(f'Deleted key: "{get_registry_key(root, path)}"')
    else:
      with winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE) as key:
        winreg.DeleteValue(key, name)
        print(f'Deleted value: "{get_registry_key(root, path, name)}"')
  except FileNotFoundError:
    print(f'[WARN] Could not find registry entry "{get_registry_key(root, path, name)}"')
  except Exception as ex:
    print(f'[ERROR] Could not delete registry entry "{get_registry_key(root, path)}": {ex}')

def add_registry_entry(root, path, name, value):
  try:
    with winreg.CreateKey(root, path) as key:
      winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
      print(f'[INFO] Set registry entry "{get_registry_key(root, path, name)}" with value "{value}"')
  except Exception as ex:
    print(f'[ERROR] Could not add registry entry for "{get_registry_key(root, path)}": {ex}')


def get_registry_key(root, path, name = None):
  root_name = HKEY_NAMES.get(root, str(root))
  return f'{root_name}\\{path}' + (f'\\{name}' if name else '')

def get_icon_path(icons_path, name):
  path = os.path.join(icons_path, f'{name}.ico')
  return path if os.path.exists(path) else None

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('\nPress Enter to exit...')

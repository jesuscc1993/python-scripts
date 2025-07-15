import json
import os
import winreg

FILE_EXTS = 'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts'

def main():
  associations = get_associations()

  for mapping in associations.get('mappings'):
    exe_path = mapping.get('exe_path')
    type_name = mapping.get('type_name')

    for ext in mapping['exts']:
      icon_path = os.path.join(associations.get('icons_path'), f'{ext.upper()}.ico')
      file_type = get_registry_value(f'.{ext}', '') or f'{ext.lower()}file'

      delete_registry_entry(f'{FILE_EXTS}\\.{ext}\\UserChoice')
      add_registry_entry(f'.{ext}', '', file_type)

      if type_name:
        add_registry_entry(f'{file_type}', 'FriendlyTypeName', type_name)

      if os.path.exists(icon_path):
        add_registry_entry(f'{file_type}\\DefaultIcon', '', f'"{icon_path}"')

      if exe_path:
        add_registry_entry(f'{file_type}\\shell\\open\\command', '', f'"{exe_path}" "%1"')

      print(f'Saved registry key: HKEY_CLASSES_ROOT\\{file_type}')

  print('Registry entries saved successfully.')

def get_associations():
  with open('./associations.json', 'r') as associations:
    return json.load(associations)

def get_registry_value(path, name):
  try:
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, path) as key:
      value, _ = winreg.QueryValueEx(key, name)
      return value
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

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('\nPress Enter to exit...')

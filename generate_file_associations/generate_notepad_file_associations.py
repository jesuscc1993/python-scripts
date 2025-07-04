import os
import winreg as reg

EXE_PATH = r'Y:\Software\Development\Notepad++\notepad++.exe'
ICONS_PATH = r'Y:\Images\Icons\Packs\File Types\ICO'
REG_ROOT = r'SOFTWARE\Classes'
FILE_EXTS = r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts'
EXTENSIONS = ['cfg', 'css', 'csv', 'gitignore', 'ini', 'js', 'json', 'less', 'lua', 'md', 'scss', 'srt', 'ts', 'txt', 'xml']

def delete_registry_entry(path):
  try:
    reg.DeleteKey(reg.HKEY_CLASSES_ROOT, path)
  except FileNotFoundError:
    pass
  except Exception as ex:
    print(f'Error deleting registry entry for {path}: {ex}')

def add_registry_entry(path, name, value):
  try:
    with reg.CreateKey(reg.HKEY_CLASSES_ROOT, path) as key:
      reg.SetValueEx(key, name, 0, reg.REG_SZ, value)
  except Exception as ex:
    print(f'Error adding registry entry for {path}: {ex}')

def main():
  for ext in EXTENSIONS:
    icon_path = f'"{os.path.join(ICONS_PATH, f"{ext.upper()}.ico")}"'
    file_type = f'{ext.lower()}file'

    delete_registry_entry(f'.{ext}\\OpenWithProgids')
    add_registry_entry(f'.{ext}', '', file_type)
    add_registry_entry(f'{file_type}\\shell\\open\\command', '', f'"{EXE_PATH}" "%1"')
    add_registry_entry(f'{file_type}\\DefaultIcon', '', icon_path)
    add_registry_entry(f'{FILE_EXTS}\\.{ext}\\UserChoice', 'Progid', file_type)

  print('Registry entries created successfully!')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('\nPress Enter to exit...')

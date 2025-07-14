import os
import winreg as reg

MAPPINGS = [
  {
    'exts': [
      'cfg',
      'conf',
      'css',
      'csv',
      'git',
      'gitignore',
      'inf',
      'ini',
      'js',
      'json',
      'less',
      'log',
      'lua',
      'md',
      'nfo',
      'sass',
      'scss',
      'srt',
      'ts',
      'txt',
      'xml',
      'yaml',
      'yml'
    ],
    'exe': r'Z:\Software\Development\Notepad++\notepad++.exe'
  },
  {
    'exts': [
      'aac',
      'flac',
      'mp3',
      'ogg',
      'wav'
    ],
    'exe': r'Z:\Software\Heavy\Multimedia\AIMP\AIMP.exe'
  }
]

ICONS_PATH = r'Z:\Images\Icons\Packs\File Types\ICO'
FILE_EXTS = r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts'

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
  for mapping in MAPPINGS:
    exe_path = mapping['exe']
    for ext in mapping['exts']:
      icon_path = f'"{os.path.join(ICONS_PATH, f"{ext.upper()}.ico")}"'
      file_type = f'{ext.lower()}file'

      delete_registry_entry(f'{FILE_EXTS}\\.{ext}\\UserChoice')
      add_registry_entry(f'.{ext}\\OpenWithProgids', '', file_type)
      add_registry_entry(f'.{ext}', '', file_type)
      add_registry_entry(f'{file_type}\\shell\\open\\command', '', f'"{exe_path}" "%1"')
      add_registry_entry(f'{file_type}\\DefaultIcon', '', icon_path)

  print('Registry entries created successfully!')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('\nPress Enter to exit...')

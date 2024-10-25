import configparser
import ctypes
import os

def main():
  parent_folder = input("Enter the path to the parent folder containing the folders or images:\n")
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    recursive = input("Run recursively in subfolders? (y/n, default 'n'):\n").strip().lower() == 'y'
    process_subfolders(parent_folder, recursive, is_root = True)

def process_subfolders(base_path, recursive, is_root = False):
  for root, dirs, files in os.walk(base_path):
    if is_root and 'desktop.ini' in files:
      process_folder(root)

    if recursive or is_root:
      for dir in dirs:
        subfolder_path = os.path.join(root, dir)
        process_subfolders(subfolder_path, recursive)

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

      if os.path.isabs(icon_resource) and folder_path in icon_resource:
        if icon_resource.endswith(',0'):
          icon_resource = icon_resource[:-2]

        relative_icon_path = os.path.relpath(icon_resource, folder_path)
        config['.ShellClassInfo']['IconResource'] = relative_icon_path

        with open(desktop_ini_path, 'w') as desktop_ini:
          config.write(desktop_ini)
        print(f"Updated IconResource in {desktop_ini_path} to relative path {relative_icon_path}")
      else:
        print(f"Skipping {folder_path}")

      ctypes.windll.kernel32.SetFileAttributesW(desktop_ini_path, 0x02 | 0x04)
  except PermissionError:
    print(f"Permission denied for {desktop_ini_path}")
  except Exception as e:
    print(f"An error occurred while processing {desktop_ini_path}: {e}")

if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
  input("\nPress Enter to exit...")
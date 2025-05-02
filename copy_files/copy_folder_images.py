import os
import shutil

FILES_TO_COPY = {
  'cover.jpg',
  'desktop.ini',
  'folder.jpg',
  'icon.ico'
}

def main():
  src_path = prompt_path('Enter the path containing the files to copy:\n')
  if src_path is None: return
  print('')

  dest_path = prompt_path('Enter the path the files will be copied to:\n')
  if dest_path is None: return
  print('')

  copy_folder_assets(src_path, dest_path)
  print('')

  print(f'Finished copying "{src_path}" to "{dest_path}".\n')
  main()

def prompt_path(prompt_message):
  path = input(prompt_message).strip('" ')
  if not path or not os.path.isdir(path):
    print(f'The specified path "{path}" is not a directory.')
    return None
  return path

def copy_folder_assets(src_path, dest_path):
  for item in os.listdir(src_path):
    item_path = os.path.join(src_path, item)
    if os.path.isdir(item_path):
      dest_folder = os.path.join(dest_path, item)
      os.makedirs(dest_folder, exist_ok=True)

      for file in os.listdir(item_path):
        if file in FILES_TO_COPY:
          shutil.copy2(os.path.join(item_path, file), os.path.join(dest_folder, file))

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')
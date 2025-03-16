import os

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders or images:\n').strip('" ')
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    delete_empty_folders(parent_folder)

def delete_empty_folders(parent_folder):
  for root, dirs, _ in os.walk(parent_folder, topdown=False):
    for dir_name in dirs:
      dir_path = os.path.join(root, dir_name)
      if is_folder_recursively_empty(dir_path):
        try:
          os.rmdir(dir_path)
          print(f'Deleted empty folder: "{dir_path}"')
        except OSError:
          pass

def is_folder_recursively_empty(dir_path):
  if os.listdir(dir_path):
    return False
  for subdir in os.listdir(dir_path):
    subdir_path = os.path.join(dir_path, subdir)
    if os.path.isdir(subdir_path) and not is_folder_recursively_empty(subdir_path):
      return False
  return True

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('Press Enter to exit...')
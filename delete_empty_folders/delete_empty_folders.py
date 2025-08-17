import os

def main():
  parent_folder = input('Enter the path to the parent folder containing the folders or images:\n').strip(' "\'')
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    delete_empty_folders(parent_folder)

def delete_empty_folders(parent_folder):
  none_deleted = True

  for root, dirs, _ in os.walk(parent_folder, topdown = False):
    for dir_name in dirs:
      dir_path = os.path.join(root, dir_name)
      try:
        os.rmdir(dir_path)
        none_deleted = False
        print(f'Deleted empty folder: "{dir_path}"')
      except OSError:
        pass
  if none_deleted:
    print('No empty folders were found.')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')
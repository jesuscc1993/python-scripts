import os
import winreg as reg

def main():
  parent_folder = input('Enter the path you want to update the subfolders for: ').strip(' "\'')
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
    return

  try:
    depth = int(input('Enter the depth for recursion (1 for root level only): ') or 1)

    view_mode = int(input(
      'Enter the view mode integer:\n'
      '  1 = Details\n'
      '  2 = Tiles\n'
      '  3 = List\n'
      '  4 = Content\n'
      '  5 = Small Icons\n'
      '  6 = Medium Icons (Mosaic)\n'
      '  7 = Large Icons\n'
      '  8 = Extra Large Icons\n'
      'Your choice: '
    ))

    update_subfolders(parent_folder, view_mode, depth)
  except ValueError:
    print('Invalid input. Please enter an integer.')

def set_folder_view(folder_path, mode):
  key_path = f'Software\\Microsoft\\Windows\\Shell\\Bags\\{hash(folder_path)}\\Shell'

  try:
    with reg.CreateKey(reg.HKEY_CURRENT_USER, key_path) as key:
      reg.SetValueEx(key, 'Mode', 0, reg.REG_DWORD, mode)
      print(f'Updated view mode to {mode} for "{folder_path}"')
  except Exception as e:
    print(f'Failed to update view mode for "{folder_path}": {e}')

def update_subfolders(base_folder, mode, depth, current_level=1):
  try:
    subfolders = [os.path.join(base_folder, name) for name in os.listdir(base_folder)
            if os.path.isdir(os.path.join(base_folder, name))]
    for subfolder in subfolders:
      set_folder_view(subfolder, mode)
      if current_level < depth:
        update_subfolders(subfolder, mode, depth, current_level + 1)
  except Exception as e:
    print(f'Error accessing folder {base_folder}: {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('\nPress Enter to exit...')
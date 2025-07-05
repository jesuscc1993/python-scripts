import os
import shutil

from _common import prompt_path

def main():
  src_path = prompt_path('Enter the path containing the files to copy:\n')
  dest_path = prompt_path('Enter the path the files will be copied to:\n')
  matches_only = input('Matches only? (y/n): ').strip().lower() == 'n'

  rename_and_copy_files(src_path, dest_path, matches_only)

  print(f'Finished copying "{src_path}" to "{dest_path}".\n')
  main()

def rename_and_copy_files(src_path, dest_path, matches_only):
  for filename in os.listdir(src_path):
    src_file = os.path.join(src_path, filename)
    dest_file = os.path.join(dest_path, filename)
    if os.path.isfile(src_file) and (os.path.exists(dest_file) or not matches_only):
      backup_file(dest_file)
      shutil.copy(src_file, dest_file)

def backup_file(file_path):
  if os.path.isfile(file_path):
    name, ext = os.path.splitext(file_path)
    new_filename = f'{name}.bak{ext}'
    bak_path = os.path.join(os.path.dirname(file_path), new_filename)

    if not os.path.isfile(bak_path):
      os.rename(file_path, bak_path)
      print(f'Saved backup file "{bak_path}".')
    else:
      print(f'Backup file "{bak_path}" already exists and will be reused.')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

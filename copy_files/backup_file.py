import os
import shutil
import sys

from _common import prompt_file, rename_with_timestamp, BACKUP_EXT, BACKUP_PATH, TIMESTAMP_FORMAT

def main():
  if len(sys.argv) > 1:
    og_file_path = sys.argv[1]
  else:
    og_file_path = prompt_file('Enter the path to the file to backup:\n')

  backup_file(og_file_path)
  print()

def backup_file(og_file_path):
  og_dir_path = os.path.dirname(og_file_path)
  og_file_name = os.path.basename(og_file_path)
  og_file_stem, src_file_ext = os.path.splitext(og_file_name)

  bak_dir_path = os.path.join(og_dir_path, BACKUP_PATH)
  bak_file_name = f'{og_file_stem}{BACKUP_EXT}{src_file_ext}'
  bak_file_path = os.path.join(bak_dir_path, bak_file_name)
  os.makedirs(bak_dir_path, exist_ok = True)

  if os.path.exists(bak_file_path):
    rename_with_timestamp(bak_dir_path, bak_file_path)

  if os.path.exists(og_file_path):
    shutil.copy2(og_file_path, bak_file_path)
    print(f'Backup up {og_file_name} as {bak_file_name}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

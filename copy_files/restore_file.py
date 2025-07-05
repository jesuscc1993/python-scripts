import os
import shutil
import sys

from _common import prompt_file, rename_with_timestamp, BACKUP_EXT, BACKUP_PATH, TIMESTAMP_FORMAT

def main():
  if len(sys.argv) > 1:
    bak_file_path = sys.argv[1]
  else:
    bak_file_path = prompt_file('Enter the path to the file to restore:\n')

  restore_file(bak_file_path)
  print()

def restore_file(bak_file_path):
  bak_dir_path = os.path.dirname(bak_file_path)
  bak_file_name = os.path.basename(bak_file_path)
  bak_file_stem, src_file_ext = os.path.splitext(bak_file_name)

  og_dir_path = os.path.normpath(bak_dir_path.replace(BACKUP_PATH, ''))
  og_file_name = f'{bak_file_stem.replace(BACKUP_EXT, '')}{src_file_ext}'
  og_file_path = os.path.join(og_dir_path, og_file_name)

  if os.path.exists(og_file_path):
    rename_with_timestamp(bak_dir_path, og_file_path)

  if os.path.exists(bak_file_path):
    shutil.copy2(bak_file_path, og_file_path)
    print(f'Restored {bak_file_name} as {og_file_name}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

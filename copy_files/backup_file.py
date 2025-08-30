import os
import shutil
import sys
import time

from _common import prompt_file, rename_with_timestamp, BACKUP_EXT, BACKUP_PATH, WATCH_INTERVAL

def main():
  if len(sys.argv) > 1:
    og_file_path = sys.argv[1]
    watch = sys.argv[2] == 'watch' if len(sys.argv) > 2 else False
  else:
    og_file_path = prompt_file('Enter the path to the file to backup:\n')

  if watch:
    while True:
      backup_file(og_file_path)
      print(f'[DEBUG] Sleeping for {WATCH_INTERVAL} seconds...')
      time.sleep(WATCH_INTERVAL)
  else:
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

  if not os.path.exists(og_file_path):
    print(f'[ERROR] File "{og_file_name}" does not exist')
    return

  if os.path.exists(bak_file_path):
    if os.path.getmtime(og_file_path) == os.path.getmtime(bak_file_path):
      print(f'[DEBUG] Skipping "{og_file_name}". Both "{og_file_name}" and "{bak_file_name}" have the same timestamp.')
      return

    rename_with_timestamp(bak_dir_path, bak_file_path)

  shutil.copy2(og_file_path, bak_file_path)
  print(f'[LOG] Backed up "{og_file_name}" as "{bak_file_name}"')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'[ERROR] An unexpected error occurred: {ex}')
    input('Press Enter to exit...')

import argparse
import os
import shutil

def copy_updated_files(src, dest):
  for src_dir, _, files in os.walk(src):
    relative_path = os.path.relpath(src_dir, src)
    dest_dir = os.path.join(dest, relative_path)
    os.makedirs(dest_dir, exist_ok=True)

    for file in files:
      src_file = os.path.join(src_dir, file)
      dest_file = os.path.join(dest_dir, file)

      if not os.path.exists(dest_file) or os.path.getmtime(src_file) > os.path.getmtime(dest_file):
        shutil.copy2(src_file, dest_file)
        print(f'Backed up "{src_file}" to "{dest_file}".')

def main():
  parser = argparse.ArgumentParser(description='Recursively copy updated files from src to dest.')
  parser.add_argument('src', type=str, help='Source directory')
  parser.add_argument('dest', type=str, help='Destination directory')
  args = parser.parse_args()
  copy_updated_files(args.src, args.dest)

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')
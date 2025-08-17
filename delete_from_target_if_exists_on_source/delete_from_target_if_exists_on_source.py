import os
import sys

def main():
  if len(sys.argv) > 2:
    src_path = sys.argv[1]
    dest_path = sys.argv[2]
  else:
    src_path = prompt_path('Enter the source path (source of truth):\n')
    dest_path = prompt_path('Enter the target path (files will be deleted here):\n')

  compare_paths_and_delete_files(src_path, dest_path)

def compare_paths_and_delete_files(src_path, dest_path):
  for root, _, files in os.walk(src_path):
    for f in files:
      path_a = os.path.join(root, f)
      path_b = path_a.replace(src_path, dest_path, 1)
      if os.path.exists(path_b):
        os.remove(path_b)
  print(f'Finished deleting from "{dest_path}" the files that already existed in "{src_path}".')

def prompt_path(prompt_message, optional = False):
  path = input(prompt_message).strip(' "\'')
  if not path or not os.path.isdir(path):
    print(f'The specified path "{path}" is not a directory.')
    if not optional: sys.exit(1)
    return None
  print('')
  return path

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

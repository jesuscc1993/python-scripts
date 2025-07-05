import os
import shutil

from _common import prompt_path

def main():
  dir_path = prompt_path('Enter the directory containing .bak files to restore:\n')

  restore_backups(dir_path)
  print(f'\nFinished restoring .bak files in "{dir_path}".\n')
  main()

def restore_backups(dir_path):
	for filename in os.listdir(dir_path):
		if '.bak.' in filename:
			bak_path = os.path.join(dir_path, filename)
			og_name = filename.replace('.bak.', '.', 1)
			og_path = os.path.join(dir_path, og_name)

			shutil.copy2(bak_path, og_path)
			print(f'Restored "{bak_path}" as "{og_path}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
    input('Press Enter to exit...')
from _common import process_parent_folder, select_parent_folder

if __name__ == '__main__':
  try:
    select_parent_folder('Enter the path to the parent folder containing the folders you want to compress:\n', process_parent_folder)
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

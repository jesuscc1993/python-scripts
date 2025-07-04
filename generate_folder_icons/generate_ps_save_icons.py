from _common import process_parent_folder

IMAGE_FILENAMES = ['ICON0.PNG']

def main():
  process_parent_folder(IMAGE_FILENAMES)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')
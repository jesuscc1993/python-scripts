import os

from mtlogger import logger

def main():
  parent_dir = input('Enter the path to the folder containing your folders:\n').strip(' "\'')

  items = [f for f in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, f)) and not f.startswith('.')]
  items.sort()

  total_items = len(items)
  num_digits = len(str(total_items))

  for index, old_name in enumerate(items, start = 1):
    new_name = f'{str(index).zfill(num_digits)}'
    old_path = os.path.join(parent_dir, old_name)
    new_path = os.path.join(parent_dir, new_name)

    os.rename(old_path, new_path)
    logger.log(f'Renamed "{old_name}" to "{new_name}".')
  logger.log(f'\nFinished processing "{parent_dir}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')
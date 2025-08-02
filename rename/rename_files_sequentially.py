import os

def main():
  parent_dir = input('Enter the path to the folder containing your files:\n').strip(' "\'')

  items = [f for f in os.listdir(parent_dir) if os.path.isfile(os.path.join(parent_dir, f)) and not f.startswith('.')]
  items.sort()

  total_items = len(items)
  num_digits = len(str(total_items))

  for index, name in enumerate(items, start = 1):
    file_extension = os.path.splitext(name)[1]
    new_name = f'{str(index).zfill(num_digits)}{file_extension}'
    old_path = os.path.join(parent_dir, name)
    new_path = os.path.join(parent_dir, new_name)

    os.rename(old_path, new_path)
    print(f'Renamed "{name}" to "{new_name}".')
  print(f'\nFinished processing "{parent_dir}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')
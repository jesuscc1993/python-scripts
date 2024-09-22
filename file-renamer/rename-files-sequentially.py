import os

def main():
  parent_folder = input("Enter the path to the folder containing your files:\n")

  files = [f for f in os.listdir(parent_folder) if os.path.isfile(os.path.join(parent_folder, f)) and not f.startswith('.')]
  files.sort()

  total_files = len(files)
  num_digits = len(str(total_files))

  for index, file_name in enumerate(files, start=1):
    file_extension = os.path.splitext(file_name)[1]
    new_file_name = f"{str(index).zfill(num_digits)}{file_extension}"
    old_file = os.path.join(parent_folder, file_name)
    new_file = os.path.join(parent_folder, new_file_name)

    os.rename(old_file, new_file)
    print(f"Renamed '{file_name}' to '{new_file_name}'.")
  print(f"\nFinished processing '{parent_folder}'.")

if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
  input("Press Enter to exit...")
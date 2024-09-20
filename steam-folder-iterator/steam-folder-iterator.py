# iterates and opens a browser tab for each steam game folder
# drop in your Steam saves folder

import os
import webbrowser

def main():
  parent_folder = input("Enter the path to the parent folder containing your Steam saves:\n")

  for filename in os.scandir(parent_folder):
    if filename.is_dir():
      webbrowser.open("https://store.steampowered.com/app/" + filename.name)

if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
  input("Press Enter to exit...")

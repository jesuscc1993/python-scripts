import os
import requests
from PIL import Image
from io import BytesIO

COVER_URL = "https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900.jpg"
JPEG_FORMAT = 'JPEG'
JPEG_QUALITY = 100
TARGET_NAME = "folder.jpg"
TARGET_WIDTH = 256

def main():
  parent_folder = input("Enter the path to the parent folder containing your Steam saves:\n")
  print("")

  for folder_name in os.listdir(parent_folder):
    folder_path = os.path.join(parent_folder, folder_name)

    if os.path.isdir(folder_path):
      process_folder(folder_path, folder_name)

  print("\nFinished generating cover images.")

def process_folder(folder_path, folder_name):
  cover_path = os.path.join(folder_path, TARGET_NAME)

  if os.path.exists(cover_path):
    print(f"Skipping {folder_name} because it already contains a {TARGET_NAME} file...")
    return

  image_url = COVER_URL.format(folder_name)
  response = requests.get(image_url)

  if response.status_code == 200:
    img = Image.open(BytesIO(response.content))

    aspect_ratio = img.height / img.width
    new_height = int(TARGET_WIDTH * aspect_ratio)

    resized_img = img.resize((TARGET_WIDTH, new_height), Image.LANCZOS)
    resized_img.save(cover_path, JPEG_FORMAT, quality=JPEG_QUALITY)
    print(f"Generated cover image for game save {folder_name} with max quality.")
  else:
    print(f"Failed to download image for {folder_name} (status code {response.status_code}).")

if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
  input("Press Enter to exit...")

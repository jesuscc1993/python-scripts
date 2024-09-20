import os
import requests
from PIL import Image
from io import BytesIO

cover_url = "https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900.jpg"
target_name = "folder.jpg"
target_width = 256

def main():
  parent_folder = input("Enter the path to the parent folder containing your Steam saves:\n")
  print("")

  for folder_name in os.listdir(parent_folder):
    folder_path = os.path.join(parent_folder, folder_name)

    if os.path.isdir(folder_path):
      download_and_resize_image(folder_name, folder_path)

  print("\nFinished generating cover images.")

def download_and_resize_image(folder_name, folder_path):
  image_url = cover_url.format(folder_name)
  response = requests.get(image_url)

  if response.status_code == 200:
    img = Image.open(BytesIO(response.content))

    aspect_ratio = img.height / img.width
    new_height = int(target_width * aspect_ratio)

    resized_img = img.resize((target_width, new_height))

    cover_image_path = os.path.join(folder_path, target_name)
    resized_img.save(cover_image_path)
    print(f"Generated cover image for game save {folder_name}.")
  else:
    print(f"Failed to download image for {folder_name} (status code {response.status_code}).")

if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
  input("Press Enter to exit...")
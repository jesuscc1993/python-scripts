import os
from PIL import Image

from _common import process_parent_folder, save_resized_image

IMAGE_FILENAME = "ICON0.PNG"

def main():
    process_parent_folder(process_folder)

def process_folder(folder_path):
    image_path = os.path.join(folder_path, IMAGE_FILENAME)

    if image_path:
        with Image.open(image_path) as img:
            save_resized_image(img, folder_path)
    else:
        print(f"No suitable image found in {folder_path}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("Press Enter to exit...")
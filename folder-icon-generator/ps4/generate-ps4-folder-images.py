import os
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

BASE_URL = "https://serialstation.com/titles/{game_id}"
DESKTOP_INI_FILENAME = "desktop.ini"
FOLDER_IMAGE_FILENAME = "folder.jpg"
FOLDER_IMAGE_FILENAME_SIZE = 256

def main():
    process_parent_folder()

def process_parent_folder():
    parent_folder = input("Enter the path to the parent folder containing the folders you want to generate icons for.\nLeave empty instead to provide and process a single folder instead.\nPARENT_FOLDER: ")

    if parent_folder == '':
        target_folder = input("\nEnter the path to the specific folder you want to generate an icon for:\nFOLDER: ")

        if not os.path.isdir(target_folder):
            print(f'The specified path "{target_folder}" is not a directory.')
            return

        print('')
        process_folder(target_folder)

    else:
        if not os.path.isdir(parent_folder):
            print(f'The specified path "{parent_folder}" is not a directory.')
            return

        print('')

    for root, dirs, _ in os.walk(parent_folder):
        for dir_name in dirs:
            item_path = os.path.join(root, dir_name)
            process_folder(item_path)

    print(f"\nFinished generating icons.")

def process_folder(folder_path):
    download_ps4_cover(os.path.basename(os.path.normpath(folder_path)), folder_path)

def download_ps4_cover(game_id, folder_path):
    url = BASE_URL.format(game_id=re.sub(r'([A-Za-z]+)(\d+)', r'\1/\2', game_id))

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        image_tag = soup.find('img', {'class': 'img-fluid'})
        if image_tag and image_tag['src']:
            image_url = image_tag['src']

            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                img = Image.open(BytesIO(image_response.content))
                img = img.resize((FOLDER_IMAGE_FILENAME_SIZE, FOLDER_IMAGE_FILENAME_SIZE), Image.LANCZOS)

                output_file_path = os.path.join(folder_path, FOLDER_IMAGE_FILENAME)
                img.save(output_file_path)
                print(f"Saved {output_file_path}")
            else:
                print(f"Failed to download image from {image_url}.")
        else:
            print(f"Cover image not found for game ID {game_id}.")
    else:
        print(f"Failed to access the {url}. Status code: {response.status_code}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("Press Enter to exit...")
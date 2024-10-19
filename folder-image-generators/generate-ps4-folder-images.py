import os
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from _common import process_parent_folder, save_resized_image

TITLE_URL = "https://serialstation.com/titles/{game_id}"

def main():
    process_parent_folder(process_folder)

def process_folder(folder_path):
    game_id = os.path.basename(os.path.normpath(folder_path))
    download_game_cover(game_id, folder_path)

def download_game_cover(game_id, folder_path):
    url = TITLE_URL.format(game_id=re.sub(r'([A-Za-z]+)(\d+)', r'\1/\2', game_id))

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        image_tag = soup.find('img', {'class': 'img-fluid'})
        if image_tag and image_tag['src']:
            image_url = image_tag['src']

            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                img = Image.open(BytesIO(image_response.content))
                save_resized_image(img, folder_path)
            else:
                print(f"Failed to download image from {image_url}.")
        else:
            print(f"Cover image not found for game ID {game_id}.")
    else:
        print(f"Failed to access {url}. Status code: {response.status_code}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("Press Enter to exit...")
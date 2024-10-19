import os
import re
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

from _common import process_parent_folder, save_resized_image

SEARCH_URL = "https://cdromance.org/?s={game_id}"

def main():
    process_parent_folder(process_folder)

def process_folder(folder_path):
    match = re.match(r'([A-Za-z]+\d+)', os.path.basename(os.path.normpath(folder_path)))

    if match:
        game_id = match.group(1)
    else:
        print(f"Could not extract a valid game ID from '{folder_path}'")
        return

    download_game_cover(game_id, folder_path)

def download_game_cover(game_id, folder_path):
    search_url = SEARCH_URL.format(game_id=game_id)
    response = requests.get(search_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        game_link = soup.select_one('.game-container a')
        if game_link and 'href' in game_link.attrs:
            game_page_url = game_link['href']

            game_response = requests.get(game_page_url)
            if game_response.status_code == 200:
                game_soup = BeautifulSoup(game_response.text, 'html.parser')

                image_tag = game_soup.select_one('.wp-post-image')
                if image_tag and 'src' in image_tag.attrs:
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
                print(f"Failed to access the game page. Status code: {game_response.status_code}")
        else:
            print(f"No game found for ID {game_id}.")
    else:
        print(f"Failed to access the search results for {game_id}. Status code: {response.status_code}")

    return False

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    input("Press Enter to exit...")
import base64
import os
import requests
import urllib.parse
from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO

MAX_COVER_WIDTH = 300
MAX_COVER_HEIGHT = 450

GOOGLE_URL_TEMPLATE = 'https://www.google.com/search?udm=2&q=site%3Aigdb.com+{query}'
GOOGLE_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}

def get_cover_image(query):
  google_url = GOOGLE_URL_TEMPLATE.format(query=urllib.parse.quote(query))
  print(f'\nSearching {google_url}...')
  response = requests.get(google_url, headers=GOOGLE_HEADERS)
  response.raise_for_status()

  soup = BeautifulSoup(response.text, 'html.parser')

  a_tags = soup.select('#iur a[href]')
  for a_tag in a_tags:
    if 'igdb.com' in a_tag['href']:
      image_tag = a_tag.find('img')
      if image_tag and image_tag.get('src'):
        return image_tag['src']

  print(f'No cover found for "{query}".')
  return None

def download_image(image_url):
  try:
    base64_data = image_url.split(',')[1]
    img_data = base64.b64decode(base64_data)
    return Image.open(BytesIO(img_data))
  except Exception as e:
    print(f'Error downloading image: {e}')
    return None

def resize_image(img):
  width, height = img.size
  ratio = min(MAX_COVER_WIDTH / width, MAX_COVER_HEIGHT / height)
  new_width = int(width * ratio)
  new_height = int(height * ratio)

  return img.resize((new_width, new_height), Image.LANCZOS)

def save_image(img, save_path):
  try:
    if img.mode != 'RGB':
      img = img.convert('RGB')
    img.save(save_path, format='JPEG')
    print(f'Saved: "{save_path}"')
  except Exception as e:
    print(f'Error saving "{img}": {e}')

def main():
  container_folder = input('Enter the path to the folder containing your games:\n').strip()
  print()

  destination_folder = input(f'Enter the path where covers should be saved to (default: {container_folder}\\_covers_):\n').strip() or f'{container_folder}\\_covers_'

  if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

  for folder_name in os.listdir(container_folder):
    folder_path = os.path.join(container_folder, folder_name)

    if os.path.isdir(folder_path):
      try:
        image_url = get_cover_image(folder_name)
        if not image_url: return
        img = download_image(image_url)
        if img:
          resized_img = resize_image(img)
          save_path = os.path.join(destination_folder, f'{folder_name}.jpg')
          save_image(resized_img, save_path)
      except Exception as e:
        print(f'Error processing folder "{folder_name}": {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('\nPress Enter to exit...')
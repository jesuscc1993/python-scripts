import os
import requests
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import re

# MAX_COVER_WIDTH = 300
# MAX_COVER_HEIGHT = 450

CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/token"
IGDB_API_URL = 'https://api.igdb.com/v4/games'
FOLDER_IMAGE_NAME = 'folder.jpg'

def get_access_token():
  response = requests.post(
    TWITCH_AUTH_URL,
    params={
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET,
      'grant_type': 'client_credentials'
    }
  )
  response.raise_for_status()
  return response.json().get('access_token')

def split_camel_case(name):
  return re.sub(r'([a-z])([A-Z])', r'\1 \2', name)

def get_cover_image(query):
  query = split_camel_case(query)
  access_token = get_access_token()
  body = f'fields name,cover.url; search "{query}"; limit 1;'

  try:
    response = requests.post(
      IGDB_API_URL,
      headers={
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
      },
      data=body
    )
    response.raise_for_status()

    games = response.json()
    cover_url = games[0].get('cover', {}).get('url') if games else None
    return f'https:{cover_url.replace("t_thumb", "t_cover_big")}' if cover_url else None

  except Exception as e:
    print(f'Error fetching cover image: {e}')
  return None

def download_image(image_url):
  try:
    response = requests.get(image_url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))
  except Exception as e:
    print(f'Error downloading image: {e}')
    return None

# def resize_image(img):
#   width, height = img.size
#   if width > MAX_COVER_WIDTH or height > MAX_COVER_HEIGHT:
#     ratio = min(MAX_COVER_WIDTH / width, MAX_COVER_HEIGHT / height)
#     new_width = int(width * ratio)
#     new_height = int(height * ratio)
#     return img.resize((new_width, new_height), Image.LANCZOS)
#   return img

def save_image(img, save_path):
  try:
    if img.mode != 'RGB':
      img = img.convert('RGB')
    img.save(save_path, format='JPEG')
    print(f'Saved: "{save_path}"')
  except Exception as e:
    print(f'Error saving "{img}": {e}')

def process_folder(folder_name, container_folder):
  folder_path = os.path.join(container_folder, folder_name)

  if os.path.isfile(os.path.join(folder_path, FOLDER_IMAGE_NAME)):
    print(f'Skipping folder "{folder_name}": "{FOLDER_IMAGE_NAME}" already exists')
    return

  if os.path.isdir(folder_path):
    try:
      image_url = get_cover_image(folder_name)
      if not image_url:
        print(f'No cover found for "{folder_name}".')
        return
      img = download_image(image_url)
      if img:
        # img = resize_image(img)
        save_path = os.path.join(folder_path, FOLDER_IMAGE_NAME)
        save_image(img, save_path)
    except Exception as e:
      print(f'Error processing folder "{folder_name}": {e}')

def main():
  container_folder = input('Enter the path to the folder containing your games:\n').strip(' "\'') or os.getcwd()

  with ThreadPoolExecutor() as executor:
    _ = [
      executor.submit(process_folder, folder_name, container_folder)
      for folder_name in os.listdir(container_folder) if os.path.isdir(os.path.join(container_folder, folder_name))
    ]

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('\nPress Enter to exit...')

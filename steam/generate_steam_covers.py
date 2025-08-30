import os
import requests
import sys
import winsound

from PIL import Image
from io import BytesIO

# settings
JPEG_FORMAT = 'JPEG'
JPEG_QUALITY = 100
TARGET_NAME = 'folder.jpg'
TARGET_HEIGHT = 168
TARGET_WIDTH = 256

COVER_URL_MAP = {
  'capsule': 'https://cdn.cloudflare.steamstatic.com/steam/apps/{}/capsule_616x353.jpg',
  'header': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/header.jpg',
  'library': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900.jpg'
}

def main():
  if len(sys.argv) > 1:
    cover_type = 'capsule'
    override_existing = False

    parent_folder = sys.argv[1]
    if len(sys.argv) > 2: cover_type = sys.argv[2]
    if len(sys.argv) > 3: override_existing = sys.argv[3].lower() == 'y'
  else:
    parent_folder, cover_type, override_existing = prompt_params()

  generate_covers(parent_folder, cover_type, override_existing)

def prompt_params():
  parent_folder = input('Enter the path to the parent folder containing your Steam saves:\n').strip(' "\'')
  print('')

  cover_type = input('Enter cover type (capsule, header, or library). Default is capsule:\n').strip().lower() or 'capsule'
  print('')

  override_existing = input('Override existing images? (y|n). Default: n:\n').strip().lower() == 'y'
  print('')

  return parent_folder, cover_type, override_existing

def generate_covers(parent_folder, cover_type, override_existing):
  cover_url = COVER_URL_MAP.get(cover_type)

  for folder_name in os.listdir(parent_folder):
    folder_path = os.path.join(parent_folder, folder_name)

    if os.path.isdir(folder_path) and folder_name.isdigit():
      process_folder(folder_path, folder_name, cover_url, override_existing)

  play_notification_sound()
  print('\n[LOG] Finished generating cover images.')

def process_folder(folder_path, folder_name, cover_url, override_existing):
  cover_path = os.path.join(folder_path, TARGET_NAME)

  if os.path.exists(cover_path) and not override_existing:
    print(f'[DEBUG] Skipping {folder_name}. A {TARGET_NAME} file is already contained within.')
    return

  image_url = cover_url.format(folder_name)
  response = requests.get(image_url)

  if response.status_code == 200:
    img = Image.open(BytesIO(response.content))

    new_scale = max(TARGET_WIDTH / img.width, TARGET_HEIGHT / img.height)
    new_width = int(img.width * new_scale)
    new_height = int(img.height * new_scale)

    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    resized_img.save(cover_path, JPEG_FORMAT, quality = JPEG_QUALITY)
    print(f'[LOG] Generated cover image for game ID {folder_name}.')
  else:
    print(f'[ERROR] Could not download image for game ID {folder_name} (status code {response.status_code}).')

def play_notification_sound():
  winsound.MessageBeep(winsound.MB_ICONASTERISK)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'[ERROR] An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

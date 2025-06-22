import os
import requests
import urllib

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from _sound_utils import play_notification_sound

def main():
  base_url = input('Enter the url to download from (replace chapter with a %s placeholder):\n').strip(' "\'')
  if not base_url:
    print(f'The url must be defined.')
    return

  css_selector = input('\nEnter the CSS selector for the image container(s):\n').strip() or 'body'

  try:
    chapter_count = int(input('\nEnter the chapter count:\n').strip())
    if chapter_count < 0:
      raise ValueError()
  except ValueError:
    print('\nERROR: Chapter count must be a positive integer.')
    return
  print('')

  download_all_chapters(base_url, css_selector, chapter_count)
  print('')

  play_notification_sound()
  print(f'Finished downloading from "{base_url}".\n')
  main()

def download_all_chapters(base_url, css_selector, chapter_count):
  files_to_process = range(1, chapter_count + 1)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc='Downloading Chapters') as progress:
    futures = [executor.submit(download_images_from_chapter, base_url, css_selector, num) for num in files_to_process]

    for future in futures:
      future.result()
      progress.update(1)

def download_images_from_chapter(base_url, css_selector, chapter_number):
  chapter_url = base_url % tuple([chapter_number] * base_url.count('%s'))
  folder = f'downloads/Ch.{pad_string(chapter_number)}'

  try:
    response = requests.get(chapter_url, timeout = 10)
    soup = BeautifulSoup(response.text, 'html.parser')
    images = []
    for container in soup.select(css_selector):
      images.extend(container.find_all('img', recursive = False))

    if images:
      os.makedirs(folder, exist_ok = True)

    for i, img in enumerate(images):
      src = img.get('src')
      if src:
        img_url = urllib.parse.urljoin(chapter_url, src)
        img_data = requests.get(img_url, timeout = 10).content
        img_ext = os.path.splitext(urllib.parse.urlparse(img_url).path)[1]
        img_name = os.path.join(folder, f'{pad_string(i + 1)}{img_ext}')
        with open(img_name, 'wb') as f:
          f.write(img_data)
  except Exception as e:
    print(f'Failed to download chapter {chapter_number}: {e}')

def pad_string(string, width = 3):
  return str(string).zfill(width)

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
    input('Press Enter to exit...')

import os
import winsound
import requests
import urllib

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from tqdm import tqdm

def main():
  base_url = Prompt.str(
    'Enter the url to download from (replace chapter with a %s placeholder)'
  )
  css_selector = Prompt.str(
    '\nEnter the CSS selector for the image container(s)',
    default='body'
  )
  chapter_count = Prompt.int(
    'Enter the chapter count',
    default = 1
  )

  download_all_chapters(base_url, css_selector, chapter_count)
  logger.log()

  winsound.MessageBeep()
  logger.success(f'Finished downloading from "{base_url}".\n')
  main()

def download_all_chapters(
  base_url: str,
  css_selector: str,
  chapter_count: int,
):
  files_to_process = range(1, chapter_count + 1)

  with ThreadPoolExecutor() as executor, tqdm(total = len(files_to_process), desc='Downloading Chapters') as progress:
    futures = [executor.submit(download_images_from_chapter, base_url, css_selector, num) for num in files_to_process]

    for future in futures:
      future.result()
      progress.update(1)

def download_images_from_chapter(
  base_url: str,
  css_selector: str,
  chapter_number: int,
):
  chapter_url = base_url % tuple([chapter_number] * base_url.count('%s'))
  folder = f'downloads/Ch.{pad_string(chapter_number)}'

  try:
    response = requests.get(chapter_url, timeout = 10)
    soup = BeautifulSoup(response.text, 'html.parser')
    images = []
    for container in soup.select(css_selector):
      images.extend(container.find_all('img', recursive = True))

    if images:
      os.makedirs(folder, exist_ok = True)
    else:
      logger.warn(f'Found no images for selector {css_selector} on URL "{chapter_url}".')

    for i, img in enumerate(images):
      src = img.get('src')
      if src:
        img_url = urllib.parse.urljoin(chapter_url, src)
        img_data = requests.get(img_url, timeout = 10).content
        img_ext = os.path.splitext(urllib.parse.urlparse(img_url).path)[1]
        img_name = os.path.join(folder, f'{pad_string(i + 1)}{img_ext}')
        with open(img_name, 'wb') as f:
          f.write(img_data)
  except Exception as ex:
    logger.error(f'Could not download chapter {chapter_number}:\n{ex}')

def pad_string(
  string: str,
  width = 3,
):
  return str(string).zfill(width)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

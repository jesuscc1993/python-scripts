import imagehash
import os
import sys

from PIL import Image
from mtlogger import logger
from mtprompt import Prompt
from send2trash import send2trash
from tqdm import tqdm

from _common import IMAGE_EXTENSIONS

HASH_THRESHOLD = 10

def main():
  if len(sys.argv) > 1:
    folder = sys.argv[1]
  else:
    folder = Prompt.dir(
      'Enter the path to the parent folder containing the chapter folders you want to clear of credits'
    )

  if len(sys.argv) > 2:
    img_path = sys.argv[2]
  else:
    img_path = Prompt.file(
      'Select the image file to match'
    )

  if len(sys.argv) > 3:
    img_spot = sys.argv[3]
  else:
    img_spot = Prompt.int(
      'Enter the position of the image to match (1 = first, -1 = last)',
      default=1
    )

  process_root(folder, img_path, img_spot)

def process_root(folder: str, img_path: str, img_spot: int):
  logger.log(f'Deleting image matches for "{folder}"...')

  ref_hash = imagehash.phash(Image.open(img_path))
  chapter_folders = sorted([
    os.path.join(folder, d) for d in os.listdir(folder)
    if os.path.isdir(os.path.join(folder, d))
  ])

  deleted = 0
  for chapter_folder in tqdm(chapter_folders):
    if process_chapter(chapter_folder, ref_hash, img_spot):
      deleted += 1

  if deleted == 0:
    logger.log('No image matches were found.')
  else:
    logger.success(f'Deleted {deleted} image {"match" if deleted == 1 else "matches"}.')

def process_chapter(chapter_folder: str, ref_hash: imagehash.ImageHash, img_spot: int):
  last_img = get_image_by_spot(chapter_folder, img_spot)
  if not last_img:
    return
  img_hash = imagehash.phash(Image.open(last_img))
  if ref_hash - img_hash <= HASH_THRESHOLD:
    send2trash(last_img)
    tqdm.write(logger.formatInfo(f'Deleted "{last_img}"'))
    return True
  return False

def get_image_by_spot(folder, spot):
  images = sorted([
    f for f in os.listdir(folder)
    if os.path.splitext(f)[1].lstrip('.').lower() in IMAGE_EXTENSIONS
  ])
  if not images:
    return None
  if spot == -1:
    return os.path.join(folder, images[-1])
  return os.path.join(folder, images[spot - 1])

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

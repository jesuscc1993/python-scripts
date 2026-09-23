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
    folder_path = sys.argv[1]
  else:
    folder_path = Prompt.dir(
      'Enter the path to the parent folder containing the chapter folders you want to clear of credits'
    )

  if len(sys.argv) > 2:
    img_path = sys.argv[2]
  else:
    img_path = Prompt.path(
      'Enter the path to the image file or folder containing the image files to match'
    )

  if len(sys.argv) > 3:
    img_spot = sys.argv[3]
  else:
    img_spot = Prompt.int(
      'Enter the position of the image to match (1 = first, -1 = last)',
      default=1
    )

  process_root(folder_path, img_path, img_spot)

def process_root(
  folder_path: str,
  img_path: str,
  img_spot: int,
):
  logger.log(f'Deleting image matches for "{folder_path}"...')

  if os.path.isdir(img_path):
    ref_paths = [
      os.path.join(img_path, f) for f in os.listdir(img_path)
      if os.path.splitext(f)[1].lstrip('.').lower() in IMAGE_EXTENSIONS
    ]
  else:
    ref_paths = [img_path]

  ref_hashes = [imagehash.phash(Image.open(p)) for p in ref_paths]
  chapter_folders = sorted([
    os.path.join(folder_path, d) for d in os.listdir(folder_path)
    if os.path.isdir(os.path.join(folder_path, d))
  ])

  deleted = 0
  for chapter_folder in tqdm(chapter_folders):
    deleted += process_chapter(chapter_folder, ref_hashes, img_spot)

  if deleted == 0:
    logger.log('No image matches were found.')
  else:
    logger.success(f'Deleted {deleted} image {"match" if deleted == 1 else "matches"}.')

def process_chapter(
  chapter_folder: str,
  ref_hashes: list[imagehash.ImageHash],
  img_spot: int,
):
  ref_hashes = list(ref_hashes)
  deleted = 0
  while ref_hashes:
    target_img = get_image_by_spot(chapter_folder, img_spot)
    if not target_img:
      break

    img_hash = imagehash.phash(Image.open(target_img))
    match = next((ref_hash for ref_hash in ref_hashes if ref_hash - img_hash <= HASH_THRESHOLD), None)
    if not match:
      break

    send2trash(target_img)
    tqdm.write(logger.format_info(f'Deleted "{target_img}"'))
    ref_hashes.remove(match)
    deleted += 1
  return deleted

def get_image_by_spot(
  folder_path: str,
  spot: int,
):
  images = sorted([
    f for f in os.listdir(folder_path)
    if os.path.splitext(f)[1].lstrip('.').lower() in IMAGE_EXTENSIONS
  ])
  if not images:
    return None
  if spot == -1:
    return os.path.join(folder_path, images[-1])
  return os.path.join(folder_path, images[spot - 1])

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

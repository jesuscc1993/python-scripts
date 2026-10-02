import os
import sys

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt, to_int
from tqdm import tqdm

from _constants import COVER_NAMES
from _common import collect_dirs_to_process, tqdm_dim

MAX_COVER_W = 300
MAX_COVER_H = 450

def main():
  if len(sys.argv) > 1:
    parent_dir = sys.argv[1]
    depth = to_int(sys.argv[2]) if len(sys.argv) > 2 else 1
  else:
    parent_dir = Prompt.dir(
      'Enter the path to the directory containing your media'
    )
    depth = Prompt.int(
      'Enter the depth for processing subfolders',
      default=1
    )

  dirs_to_process = collect_dirs_to_process(parent_dir, depth)

  with ThreadPoolExecutor() as executor, tqdm(total = len(dirs_to_process), desc = f'Processing "{parent_dir}"') as progress:
    for _ in executor.map(process_dir, dirs_to_process):
      progress.update(1)

  logger.success(f'Finished downsizing covers in "{parent_dir}".')

def find_cover(
  dir: str,
):
  for cover_name in COVER_NAMES:
    path = os.path.join(dir, cover_name)
    if os.path.isfile(path):
      return path
  return None

def process_dir(
  dir: str,
):
  dir_name = os.path.basename(dir)
  cover_img_path = find_cover(dir)

  if cover_img_path is None:
    tqdm_dim(f'Skipping "{dir_name}". No cover found.')
    return

  img = Image.open(cover_img_path)
  if img.width <= MAX_COVER_W and img.height <= MAX_COVER_H:
    tqdm_dim(f'Skipping "{dir_name}". Cover does not exceed resolution limits.')
    return

  resized_img = downsize_cover(img, MAX_COVER_W, MAX_COVER_H)
  img.close()

  webp_cover_img_path = os.path.splitext(cover_img_path)[0] + '.webp'
  resized_img.save(webp_cover_img_path, format='WEBP', quality=100)
  if webp_cover_img_path != cover_img_path:
    os.remove(cover_img_path)

  tqdm.write(logger.format_debug(f'Downsized cover for "{dir_name}".'))

def downsize_cover(
  img: Image.Image,
  max_w: int,
  max_h: int,
):
  scale = max(max_w / img.width, max_h / img.height)
  return img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout=True)
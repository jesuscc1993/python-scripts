import numpy
import sys

from PIL import Image
from mtlogger import LogLevel, logger
from mtprompt import Prompt
from mtvalidation import to_dir

from _common import process_folder_images, select_parent_folder
from _image_utils import save_image_to_path

LOGGING_ENABLED = False

LEVEL_TOLERANCE = 5
MIN_PERCENTILE = 5
MAX_PERCENTILE = 99.9
SCAN_AREA = 0.8

PROFILES = {
  'STRONG': [51, 204],
  'MEDIUM': [24, 224],
  'MINIMUM': [0, 255],
}
BLACK_THRESHOLD, WHITE_THRESHOLD = PROFILES['MINIMUM']


def main():
  logger.set_level(LogLevel.WARN)

  if len(sys.argv) > 1:
    process_parent_folder(to_dir(sys.argv[1]))
  else:
    select_parent_folder(
      'Enter the path to the parent folder containing the folders or images you want to level shift:\n',
      process_parent_folder,
    )


def process_parent_folder(
  folder_path: str,
):
  process_folder_images(folder_path, process_image)


def process_image(
  file_path: str,
):
  img = Image.open(file_path)
  if not is_grayscale(img):
    logger.write(
      LogLevel.TRACE,
      logger.format_trace(
        f'  Skipping "${file_path}". Image is not grayscale.'
      ),
    )
    return

  arr = numpy.array(img.convert('L'), dtype=numpy.float32)
  arr_min, arr_max = get_min_max(arr, SCAN_AREA)

  if (
    arr_min <= BLACK_THRESHOLD + LEVEL_TOLERANCE
    and arr_max >= WHITE_THRESHOLD - LEVEL_TOLERANCE
  ):
    logger.write(
      LogLevel.TRACE,
      logger.format_trace(
        f'  Skipping "${file_path}". Image already contains pure black and white values.'
      ),
    )
    return

  if arr_max != arr_min:
    scaled = (arr - arr_min) * (
      (WHITE_THRESHOLD - BLACK_THRESHOLD) / (arr_max - arr_min)
    ) + BLACK_THRESHOLD
  else:
    scaled = arr.copy()

  scaled = numpy.clip(scaled, BLACK_THRESHOLD, WHITE_THRESHOLD)
  scaled = (scaled - BLACK_THRESHOLD) * (
    255 / (WHITE_THRESHOLD - BLACK_THRESHOLD)
  )
  scaled = numpy.clip(scaled, 0, 255).astype(numpy.uint8)

  out_img = Image.fromarray(scaled)
  save_image_to_path(out_img, file_path, log=True)


def is_grayscale(
  img: Image.Image,
  tolerance=5,
):
  if img.mode == 'L':
    return True
  if img.mode in ['RGB', 'RGBA']:
    arr = numpy.array(img)
    if img.mode == 'RGBA':
      arr = arr[:, :, :3]
    diff = arr.max(axis=2) - arr.min(axis=2)
    return numpy.all(diff <= tolerance)
  return False


def get_min_max(
  array: numpy.ndarray,
  scan_area=1,
):
  if scan_area <= 0 or scan_area >= 1:
    cropped_arr = array
  else:
    h, w = array.shape
    h_crop = int(h * (1 - scan_area) / 2)
    w_crop = int(w * (1 - scan_area) / 2)
    cropped_arr = array[h_crop : h - h_crop, w_crop : w - w_crop]

  return numpy.percentile(cropped_arr, [MIN_PERCENTILE, MAX_PERCENTILE])


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)
    Prompt.enter_to_exit()

import argparse

from mtlogger import logger
from mtprompt import Prompt, to_dir, to_list, to_path

from generate_images_with_background import generate_images_with_background

ANDROID_CANVAS_SIZE = 192
ANDROID_FOREGROUND_SCALE = 0.67
ANDROID_BACKGROUND_SCALE = 0.92

def main():
  args = parse_args()
  has_args = any(value is not None for value in vars(args).values())

  if has_args:
    foreground_folder = to_dir(args.foreground)
    output_folder = to_dir(args.output)
    background_path = to_path(args.background)
    tints = to_list(args.tint) if args.tint else None
  else:
    foreground_folder = Prompt.dir(
      'Enter the path to the folder containing the foreground images you want to add a background to'
    )
    output_folder = Prompt.dir(
      'Enter the path to the output folder'
    )
    background_path = Prompt.path(
      'Enter the path to the background image or a folder of background images'
    )
    tints = Prompt.list(
      'Enter a comma-separated list of tint colors, to apply to the background(s)',
      optional=True
    )

  generate_images_with_background(
    foreground_folder,
    output_folder,
    background_path,
    tints,
    ANDROID_CANVAS_SIZE,
    ANDROID_FOREGROUND_SCALE,
    ANDROID_BACKGROUND_SCALE
  )

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--foreground')
  parser.add_argument('-o', '--output')
  parser.add_argument('-b', '--background')
  parser.add_argument('-t', '--tint')
  return parser.parse_args()

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit(timeout = True)
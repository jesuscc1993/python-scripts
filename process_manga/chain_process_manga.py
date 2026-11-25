import sys

from mtlogger import logger
from mtprompt import Prompt, to_dir

from _common import select_parent_folder, run_scripts_in_sequence


def main():
  if len(sys.argv) > 1:
    process_parent_folder(to_dir(sys.argv[1]))
  else:
    select_parent_folder(None, process_parent_folder)


def process_parent_folder(
  parent_folder_path: str,
):
  crop = Prompt.bool('\nCrop borders and/or downscale?', default=True)

  script_names = ['../compress/extract_archives $dir']

  if crop:
    script_names.append('crop_borders $dir')

  script_names.extend(
    [
      '../compress/compress_folders $dir ZIP Y',
      'rename_items $dir',
      '../rename/rename_zip_to_cbz $dir',
    ]
  )

  run_scripts_in_sequence(script_names, parent_folder_path)


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

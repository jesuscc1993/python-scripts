import os
import shutil
import sys
import time

from mtattr import Attr
from mtlogger import logger
from mtprompt import Prompt

from _common import (
  rename_with_timestamp,
  BACKUP_EXT,
  BACKUP_PATH,
  WATCH_INTERVAL,
)


def main():
  if len(sys.argv) > 1:
    og_file_path = sys.argv[1]
    watch = sys.argv[2] == 'watch' if len(sys.argv) > 2 else False
  else:
    og_file_path = Prompt.file('Enter the path to the file to backup')
    watch = False

  if watch:
    while True:
      backup_up = backup_file(og_file_path)
      logger.debug(
        f'Sleeping for {WATCH_INTERVAL} seconds...'
        if backup_up
        else f'Retrying in {WATCH_INTERVAL} seconds...'
      )
      time.sleep(WATCH_INTERVAL)
  else:
    backup_file(og_file_path)


def backup_file(
  og_file_path: str,
):
  og_dir_path = os.path.dirname(og_file_path)
  og_file_name = os.path.basename(og_file_path)
  og_file_stem, src_file_ext = os.path.splitext(og_file_name)

  bak_dir_path = os.path.join(og_dir_path, BACKUP_PATH)
  bak_file_name = f'{og_file_stem}{BACKUP_EXT}{src_file_ext}'
  bak_file_path = os.path.join(bak_dir_path, bak_file_name)
  tmp_file_path = f'{bak_file_path}.tmp'

  stamped_file_path = None

  if not os.path.exists(og_file_path):
    logger.error(f'File "{og_file_name}" does not exist')
    return False

  try:
    if os.path.exists(bak_file_path) and os.path.getmtime(
      og_file_path
    ) == os.path.getmtime(bak_file_path):
      logger.trace(
        f'Skipping "{og_file_name}". Both "{og_file_name}" and "{bak_file_name}" have the same timestamp.'
      )
      return True

    src_mtime = os.path.getmtime(og_file_path)
    os.makedirs(bak_dir_path, exist_ok=True)

    shutil.copy2(og_file_path, tmp_file_path)
    Attr.hide(tmp_file_path)

    if src_mtime != os.path.getmtime(og_file_path):
      raise RuntimeError('File changed during backup')

    if os.path.exists(bak_file_path):
      stamped_file_path = rename_with_timestamp(bak_dir_path, bak_file_path)

    os.replace(tmp_file_path, bak_file_path)

  except Exception as ex:
    try:
      if stamped_file_path:
        os.replace(stamped_file_path, bak_file_path)

      if os.path.exists(tmp_file_path):
        os.remove(tmp_file_path)

    except Exception as rollback_ex:
      logger.error(
        f'Failed to clean up or restore backup "{bak_file_name}":\n{rollback_ex}'
      )

    logger.error(f'Failed to back up "{og_file_path}":\n{ex}')
    return False

  logger.success(f'Backed up "{og_file_name}" as "{bak_file_name}"')
  return True


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

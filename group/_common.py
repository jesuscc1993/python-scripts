import os

import shutil
import winsound

from mtlogger import logger

def select_parent_folder(prompt, callback):
  parent_folder = input(prompt).strip(' "\'')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    logger.error(f'The specified path "{parent_folder}" is not a directory.')
  else:
    callback(parent_folder)
    play_notification_sound()
    logger.log(f'Finished processing "{parent_folder}".\n')
  select_parent_folder(prompt, callback)

def play_notification_sound():
  winsound.MessageBeep(winsound.MB_ICONASTERISK)

def process_file(params):
  src, target_folder = params
  dest = os.path.join(target_folder, os.path.basename(src))
  shutil.move(src, dest)
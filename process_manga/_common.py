import os

from _sound_utils import play_notification_sound

def select_parent_folder(prompt, callback):
  parent_folder = input(prompt).strip('" ')
  if not parent_folder:
    return
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    callback(parent_folder)
    play_notification_sound()
    print(f'Finished processing "{parent_folder}".\n')
  select_parent_folder(prompt, callback)

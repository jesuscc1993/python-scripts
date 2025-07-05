import os
import sys

def prompt_path(prompt_message, optional = False):
  path = input(prompt_message).strip(' "\'')
  if not path or not os.path.isdir(path):
    print(f'The specified path "{path}" is not a directory.')
    if not optional: sys.exit(1)
    return None
  print('')
  return path
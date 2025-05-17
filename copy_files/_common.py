import os

def prompt_path(prompt_message):
  path = input(prompt_message).strip(' "\'')
  if not path or not os.path.isdir(path):
    print(f'The specified path "{path}" is not a directory.')
    return None
  return path
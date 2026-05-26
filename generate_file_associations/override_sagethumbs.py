import winreg

from mtlogger import logger
from mtprompt import Prompt

IMAGE_EXTENSIONS = [
  'bmp',
  'dds',
  'gif',
  'ico',
  'jpeg',
  'jpg',
  'png',
  'svg',
  'tga',
  'tif',
  'tiff',
  'webp'
]

def main():
  for ext in IMAGE_EXTENSIONS:
    update_key(f'SageThumbsImage.{ext}')
    # update generic class too in case sagethumbs is nto set up for this particular extension
    update_key(f'{ext}file')

def update_key(key_name):
  try:
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_name, 0, winreg.KEY_SET_VALUE) as subkey:
      winreg.SetValueEx(subkey, '', 0, winreg.REG_SZ, 'Image File')
      logger.debug(f'Updated "{key_name}".')
  except FileNotFoundError:
    pass

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enter_to_exit()

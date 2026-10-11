import winreg

from mtlogger import logger
from mtprompt import Prompt

IMAGE_FILE_TYPE_NAME = 'Image File'

IMAGE_EXTENSIONS = [
  'bmp',
  'cur',
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
  'webp',
]


def main():
  for ext in IMAGE_EXTENSIONS:
    # update generic class too in case SageThumbs is not set up for this particular extension
    update_association_file_name(f'{ext}file', ext)
    update_association_file_name(f'SageThumbsImage.{ext}', ext)


def update_association_file_name(
  key_name: str,
  ext: str,
):
  try:
    with winreg.OpenKey(
      winreg.HKEY_CLASSES_ROOT, key_name, 0, winreg.KEY_SET_VALUE
    ) as subkey:
      file_type_name = get_association_file_name(ext)
      winreg.SetValueEx(subkey, '', 0, winreg.REG_SZ, file_type_name)
      logger.debug(f'Updated "{key_name}".')
  except FileNotFoundError:
    pass


def get_association_file_name(
  ext: str,
):
  # return f'{ext} Image File'
  return IMAGE_FILE_TYPE_NAME


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

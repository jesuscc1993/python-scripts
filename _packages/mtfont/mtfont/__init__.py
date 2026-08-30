import os

from PIL import ImageFont
from mtlogger import LogLevel, Logger

class Font:

  logger = Logger(LogLevel.ERROR)

  @staticmethod
  def find_by_name(
    name: str,
  ):
    user_fonts = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts', name)
    if os.path.exists(user_fonts):
      Font.logger.trace(f'Found font "{name}" in user fonts.')
      return user_fonts

    system_fonts = os.path.join(os.environ.get('WINDIR', ''), 'Fonts', name)
    if os.path.exists(system_fonts):
      Font.logger.trace(f'Found font "{name}" in system fonts.')
      return system_fonts

    return None

  @staticmethod
  def load_by_name(
    name: str,
    size: int,
  ):
    return Font.load_by_path(Font.find_by_name(name), size)

  @staticmethod
  def load_by_path(
    path: str,
    size: int,
  ):
    try:
      return ImageFont.truetype(path, size)

    except Exception:
      Font.logger.warn(f'Failed to load font "{path}". Using default font instead.')
      return ImageFont.load_default(size)

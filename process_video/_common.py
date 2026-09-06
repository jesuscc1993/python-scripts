import re

from mtfs import read_text_file, write_text_file

from _constants import ENCODING, FONT_ATTRIBUTES, STRIP_SETTINGS

def add_missing_spaces_to_subs_file(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)
  content = re.sub(r'(?<=[a-záéíóúüñ])([.,;:!?]+)([A-ZÁÉÍÓÚÜÑ])', r'\1 \2', content)
  content = re.sub(r'(?<=\S)(\.\.\.)(?=[A-ZÁÉÍÓÚÜÑ])', r'\1 ', content)

  write_text_file(file_path, content, ENCODING)

def strip_tags_from_subs_file(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)
  if STRIP_SETTINGS.get('fonts'):
    content = re.sub(r'</?font\b[^>]*>', '', content, flags = re.IGNORECASE)
  else:
    for attr in FONT_ATTRIBUTES:
      if STRIP_SETTINGS.get(attr):
        content = strip_attribute(content, attr)

  write_text_file(file_path, content, ENCODING)

def fix_invalid_chars_in_subs_file(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)
  content = content.replace('\u00ce\u00bd', 'v').replace('\u00ce\u009d', 'V')
  write_text_file(file_path, content, ENCODING)

def strip_attribute(
  content: str,
  attribute: str,
):
  return re.sub(rf'\s*\b{attribute}=["\'][^"\']*["\']', '', content, flags = re.IGNORECASE)

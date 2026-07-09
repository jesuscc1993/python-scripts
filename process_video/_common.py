import re

ENCODING = 'latin-1'
FONT_ATTRIBUTES = ['color', 'face', 'size']

STRIP_SETTINGS = {
  'fonts': True,
  'color': False,
  'face': False,
  'size': False,
}

def add_missing_spaces(file_path):
  with open(file_path, 'r', encoding = ENCODING, errors = 'replace') as f:
    content = f.read()
  content = re.sub(r'(?<=[a-záéíóúüñ])([.,;:!?]+)([A-ZÁÉÍÓÚÜÑ])', r'\1 \2', content)
  with open(file_path, 'w', encoding = ENCODING) as f:
    f.write(content)

def strip_tags_from_subs_file(file_path):
  with open(file_path, 'r', encoding = ENCODING, errors = 'replace') as f:
    content = f.read()
  if STRIP_SETTINGS.get('fonts'):
    content = re.sub(r'</?font\b[^>]*>', '', content, flags = re.IGNORECASE)
  else:
    for attr in FONT_ATTRIBUTES:
      if STRIP_SETTINGS.get(attr):
        content = strip_attribute(content, attr)
  with open(file_path, 'w', encoding = ENCODING) as f:
    f.write(content)

def strip_attribute(content, attribute):
  return re.sub(rf'\s*\b{attribute}=["\'][^"\']*["\']', '', content, flags = re.IGNORECASE)

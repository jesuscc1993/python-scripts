import re

ENCODING = 'latin-1'

def add_missing_spaces(file_path):
  with open(file_path, 'r', encoding = ENCODING, errors = 'replace') as f:
    content = f.read()
  content = re.sub(r'(?<=[a-záéíóúüñ])([.,;:!?]+)([A-ZÁÉÍÓÚÜÑ])', r'\1 \2', content)
  with open(file_path, 'w', encoding = ENCODING) as f:
    f.write(content)

def strip_tags_from_subs_file(file_path):
  with open(file_path, 'r', encoding = ENCODING, errors = 'replace') as f:
    content = f.read()
  content = re.sub(r'</?font\b[^>]*>', '', content, flags = re.IGNORECASE)
  with open(file_path, 'w', encoding = ENCODING) as f:
    f.write(content)

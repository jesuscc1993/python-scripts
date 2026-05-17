import re
import sys

from mtlogger import logger
from pathlib import Path

# problematic with things like ?!, ..., etc.
def add_missing_spaces(file_path):
  with open(file_path, 'r', encoding = 'utf-8', errors = 'replace') as f:
    content = f.read()
  content = re.sub(r'((?:[,!?;:])|(?:(?<!\.)\.(?!\.)))([^\s\d\'"\)\]\-<])', r'\1 \2', content)
  with open(file_path, 'w', encoding = 'utf-8') as f:
    f.write(content)

def strip_tags_from_subs_file(file_path):
  with open(file_path, 'r', encoding = 'utf-8', errors = 'replace') as f:
    content = f.read()
  content = re.sub(r'</?font\b[^>]*>', '', content, flags = re.IGNORECASE)
  with open(file_path, 'w', encoding = 'utf-8') as f:
    f.write(content)

def prompt_path(prompt_message, optional = False):
  path = input(prompt_message).strip(' "\'')
  if not Path(path).exists():
    logger.error(f'The specified path "{path}" does not exist.')
    if not optional: sys.exit(1)
    return None
  logger.log()
  return path

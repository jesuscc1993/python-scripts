import re

from mtfs import read_text_file, write_text_file

from _constants import ENCODING, HTML_FONT_ATTRIBUTES
from _settings import SETTINGS

def post_process_html_subtitles(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)

  if SETTINGS['strip_settings']['enabled']:
    content = strip_html_tags(content)
  if SETTINGS['replace_color'] and not SETTINGS['strip_settings']['color']:
    content = replace_html_text_color(content)

  write_text_file(file_path, content, ENCODING)

def replace_html_text_color(
  content: str,
):
  return re.sub(
    rf'(color=["\'])#?{SETTINGS["lookup_text_color"]}(["\'])',
    rf'\g<1>#{SETTINGS["preferred_text_color"]}\g<2>',
    content,
    flags = re.IGNORECASE
  )

def strip_html_tags(
  content: str,
):
  if SETTINGS['strip_settings'].get('fonts'):
    content = re.sub(r'</?font\b[^>]*>', '', content, flags = re.IGNORECASE)
  else:
    for attr in HTML_FONT_ATTRIBUTES:
      if SETTINGS['strip_settings'].get(attr):
        content = strip_attribute(content, attr)

  return content

def strip_attribute(
  content: str,
  attribute: str,
):
  return re.sub(
    rf'\s*\b{attribute}=["\'][^"\']*["\']',
    '',
    content,
    flags = re.IGNORECASE
  )

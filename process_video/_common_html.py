import re

from mtfs import read_text_file, write_text_file

from _constants import ENCODING, HTML_FONT_ATTRIBUTES, HTML_SUPPORTED_TAGS
from _settings import SETTINGS


def post_process_html_subtitles(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)
  content = strip_conversion_leftovers(content)

  if SETTINGS['strip_settings']['enabled']:
    content = strip_html_tags(content)
  if (
    SETTINGS['replace_foreground_color']
    and not SETTINGS['strip_settings']['color']
  ):
    content = replace_html_foreground_color(content)
  if SETTINGS['force_font'] and not SETTINGS['strip_settings']['fonts']:
    content = force_html_font(content)

  write_text_file(file_path, content, ENCODING)


def strip_conversion_leftovers(
  content: str,
):
  # content = re.sub(r'\{\\an[1-9]\}', '', content)
  return content


def replace_html_foreground_color(
  content: str,
):
  for lookup_foreground_color in SETTINGS['lookup_foreground_colors']:
    content = re.sub(
      rf'(color=["\'])#?{re.escape(lookup_foreground_color[:6])}(?:[0-9A-Fa-f]{{2}})?(["\'])',
      rf'\g<1>#{SETTINGS["preferred_foreground_color"]}\g<2>',
      content,
      flags=re.IGNORECASE,
    )
  return content


def force_html_font(
  content: str,
):
  def replace_face_attribute(
    match: re.Match,
  ):
    tag = match.group(0)
    if re.search(r'\bface=["\'][^"\']*["\']', tag, flags=re.IGNORECASE):
      return re.sub(
        r'face=["\'][^"\']*["\']',
        f'face="{SETTINGS["preferred_font"]}"',
        tag,
        flags=re.IGNORECASE,
      )
    return tag[:-1] + f' face="{SETTINGS["preferred_font"]}">'

  return re.sub(
    r'<font\b[^>]*>', replace_face_attribute, content, flags=re.IGNORECASE
  )


def strip_html_tags(
  content: str,
):
  content = strip_unsupported_tags(content)

  if SETTINGS['strip_settings'].get('fonts'):
    content = re.sub(r'</?font\b[^>]*>', '', content, flags=re.IGNORECASE)
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
    rf'\s*\b{attribute}=["\'][^"\']*["\']', '', content, flags=re.IGNORECASE
  )


def strip_unsupported_tags(
  content: str,
):
  supported_tags_pattern = '|'.join(HTML_SUPPORTED_TAGS)
  return re.sub(
    rf'</?(?!(?:{supported_tags_pattern})\b)\w+\b[^>]*>',
    '',
    content,
    flags=re.IGNORECASE,
  )

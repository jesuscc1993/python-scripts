import re

from functools import partial
from mtfs import read_text_file, write_text_file

from _constants import ASS_STYLE_FONTNAME_FIELD, ASS_STYLE_FORMAT_LINE_PATTERN, ASS_STYLE_LINE_PATTERN, ASS_STYLE_OUTLINE_COLOUR_FIELD, ASS_STYLE_OUTLINE_FIELD, ASS_STYLE_PRIMARY_COLOUR_FIELD, ENCODING, HEX_COLOUR_VALUE_PATTERN, HEX_DIGIT_PATTERN
from _settings import SETTINGS

def rgb_to_bgr(
  rgb_color: str,
):
  return rgb_color[4:6] + rgb_color[2:4] + rgb_color[0:2]

def post_process_ass_subtitles(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)

  if SETTINGS['replace_color']:
    content = re.sub(
      rf'(&H{HEX_DIGIT_PATTERN}{{0,2}}){rgb_to_bgr(SETTINGS["lookup_text_color"])}',
      rf'\g<1>{rgb_to_bgr(SETTINGS["preferred_text_color"])}',
      content,
      flags = re.IGNORECASE
    )

  field_indices = build_ass_style_field_indices(content)

  if SETTINGS['force_text_color']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_colour,
        field_indices=field_indices,
        field_name=ASS_STYLE_PRIMARY_COLOUR_FIELD,
        replacement_color=rgb_to_bgr(SETTINGS['preferred_text_color'])
      ),
      content
    )

  if SETTINGS['force_border_color']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_colour,
        field_indices=field_indices,
        condition_field_name=ASS_STYLE_OUTLINE_FIELD,
        field_name=ASS_STYLE_OUTLINE_COLOUR_FIELD,
        replacement_color=rgb_to_bgr(SETTINGS['preferred_border_color'])
      ),
      content
    )

  if SETTINGS['force_font']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_field,
        field_indices=field_indices,
        field_name=ASS_STYLE_FONTNAME_FIELD,
        replacement_value=SETTINGS['preferred_font']
      ),
      content
    )

  write_text_file(file_path, content, ENCODING)

def build_ass_style_field_indices(
  content: str,
) -> dict[str, int]:
  for match in re.finditer(ASS_STYLE_FORMAT_LINE_PATTERN, content):
    names = [name.strip() for name in match.group(1).split(',')]
    if ASS_STYLE_PRIMARY_COLOUR_FIELD in names:
      return {name: index for index, name in enumerate(names)}
  return {}

def replace_ass_style_colour(
  match: re.Match,
  field_indices: dict[str, int],
  field_name: str,
  replacement_color: str,
  condition_field_name: str | None = None,
):
  field_index = field_indices.get(field_name)
  condition_index = field_indices.get(condition_field_name) if condition_field_name else None
  if field_index is None or (condition_field_name is not None and condition_index is None):
    return match.group(0)

  fields = match.group(1).split(',')
  if len(fields) <= max(field_index, condition_index or 0):
    return match.group(0)
  if condition_index is None or float(fields[condition_index]) > 0:
    fields[field_index] = re.sub(HEX_COLOUR_VALUE_PATTERN, replacement_color, fields[field_index])
  return 'Style: ' + ','.join(fields)

def replace_ass_style_field(
  match: re.Match,
  field_indices: dict[str, int],
  field_name: str,
  replacement_value: str,
):
  field_index = field_indices.get(field_name)
  if field_index is None:
    return match.group(0)

  fields = match.group(1).split(',')
  if len(fields) <= field_index:
    return match.group(0)
  fields[field_index] = replacement_value
  return 'Style: ' + ','.join(fields)

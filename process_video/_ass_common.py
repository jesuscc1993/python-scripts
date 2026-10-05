import re

from functools import partial
from mtfs import read_text_file, write_text_file

from _constants import ASS_STYLE_FORMAT_LINE_PATTERN, ASS_STYLE_LINE_PATTERN, ASS_STYLE_OUTLINE_COLOUR_FIELD, ASS_STYLE_OUTLINE_FIELD, ASS_STYLE_PRIMARY_COLOUR_FIELD, ENCODING, FORCE_BORDER_COLOR, FORCE_TEXT_COLOR, PREFERRED_BORDER_COLOR, HEX_COLOUR_VALUE_PATTERN, HEX_DIGIT_PATTERN, LOOKUP_TEXT_COLOR, REPLACE_COLOR, PREFERRED_TEXT_COLOR

def post_process_ass_file(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)

  if REPLACE_COLOR:
    content = re.sub(
      rf'(&H{HEX_DIGIT_PATTERN}{{0,2}}){LOOKUP_TEXT_COLOR}',
      rf'\g<1>{PREFERRED_TEXT_COLOR}',
      content,
      flags = re.IGNORECASE
    )

  field_indices = build_ass_style_field_indices(content)

  if FORCE_TEXT_COLOR:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_colour,
        field_indices=field_indices,
        field_name=ASS_STYLE_PRIMARY_COLOUR_FIELD,
        replacement_color=PREFERRED_TEXT_COLOR
      ),
      content
    )

  if FORCE_BORDER_COLOR:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_colour,
        field_indices=field_indices,
        condition_field_name=ASS_STYLE_OUTLINE_FIELD,
        field_name=ASS_STYLE_OUTLINE_COLOUR_FIELD,
        replacement_color=PREFERRED_BORDER_COLOR
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

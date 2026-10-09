import re

from functools import partial
from mtfs import read_text_file, write_text_file

from _constants import ASS_STYLE_BACK_COLOUR_FIELD, ASS_STYLE_FONTNAME_FIELD, ASS_STYLE_FORMAT_LINE_PATTERN, ASS_STYLE_LINE_PATTERN, ASS_STYLE_OUTLINE_COLOUR_FIELD, ASS_STYLE_OUTLINE_FIELD, ASS_STYLE_PRIMARY_COLOUR_FIELD, ASS_STYLE_SHADOW_FIELD, ENCODING, HEX_COLOUR_VALUE_PATTERN, HEX_DIGIT_PATTERN
from _settings import SETTINGS

def rgba_to_bgra(
  rgba_color: str,
):
  rgb_color = rgba_color[:6]
  bgr_color = rgb_color[4:6] + rgb_color[2:4] + rgb_color[0:2]
  if len(rgba_color) == 6:
    return bgr_color
  ass_alpha = 255 - int(rgba_color[6:8], 16)
  return f'{ass_alpha:02X}{bgr_color}'

def post_process_ass_subtitles(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)

  if SETTINGS['replace_foreground_color']:
    for lookup_foreground_color in SETTINGS['lookup_foreground_colors']:
      preferred_foreground_color = SETTINGS['preferred_foreground_color']
      content = re.sub(
        rf'&H({HEX_DIGIT_PATTERN}{{0,2}}){lookup_foreground_color[4:6]}{lookup_foreground_color[2:4]}{lookup_foreground_color[0:2]}',
        lambda match: f'&H{match.group(1) if len(preferred_foreground_color) == 6 else ""}{rgba_to_bgra(preferred_foreground_color)}',
        content,
        flags = re.IGNORECASE
      )

  field_indices = build_ass_style_field_indices(content)

  if SETTINGS['replace_outline_color']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_colour,
        field_indices=field_indices,
        field_name=ASS_STYLE_OUTLINE_COLOUR_FIELD,
        replacement_color=rgba_to_bgra(SETTINGS['preferred_outline_color']),
        lookup_colors=SETTINGS['lookup_outline_colors']
      ),
      content
    )

  if SETTINGS['replace_background_color']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_colour,
        field_indices=field_indices,
        field_name=ASS_STYLE_BACK_COLOUR_FIELD,
        replacement_color=rgba_to_bgra(SETTINGS['preferred_background_color']),
        lookup_colors=SETTINGS['lookup_background_colors']
      ),
      content
    )

  if SETTINGS['force_foreground_color']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_colour,
        field_indices=field_indices,
        field_name=ASS_STYLE_PRIMARY_COLOUR_FIELD,
        replacement_color=rgba_to_bgra(SETTINGS['preferred_foreground_color'])
      ),
      content
    )

  if SETTINGS['force_outline_color']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_colour,
        field_indices=field_indices,
        condition_field_name=ASS_STYLE_OUTLINE_FIELD,
        field_name=ASS_STYLE_OUTLINE_COLOUR_FIELD,
        replacement_color=rgba_to_bgra(SETTINGS['preferred_outline_color'])
      ),
      content
    )

  if SETTINGS['force_background_color']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_colour,
        field_indices=field_indices,
        field_name=ASS_STYLE_BACK_COLOUR_FIELD,
        replacement_color=rgba_to_bgra(SETTINGS['preferred_background_color'])
      ),
      content
    )

  if SETTINGS['replace_font']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_field,
        field_indices=field_indices,
        field_name=ASS_STYLE_FONTNAME_FIELD,
        replacement_value=SETTINGS['preferred_font'],
        lookup_values=SETTINGS['lookup_fonts']
      ),
      content
    )

  if SETTINGS['force_outline_thickness_and_shadow_offset']:
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_field,
        field_indices=field_indices,
        field_name=ASS_STYLE_OUTLINE_FIELD,
        replacement_value=SETTINGS['preferred_outline_thickness']
      ),
      content
    )
    content = re.sub(
      ASS_STYLE_LINE_PATTERN,
      partial(
        replace_ass_style_field,
        field_indices=field_indices,
        field_name=ASS_STYLE_SHADOW_FIELD,
        replacement_value=SETTINGS['preferred_shadow_offset']
      ),
      content
    )
    content = set_scaled_border_and_shadow_off(content)

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

def set_scaled_border_and_shadow_off(
  content: str,
):
  lines = content.splitlines(keepends=True)
  line_ending = '\r\n' if '\r\n' in content else '\n'
  script_info_index = next(
    (index for index, line in enumerate(lines) if line.strip().casefold() == '[script info]'),
    None
  )

  if script_info_index is None:
    return f'[Script Info]{line_ending}ScaledBorderAndShadow: no{line_ending}{line_ending}{content}'

  section_end_index = next(
    (index for index in range(script_info_index + 1, len(lines)) if lines[index].strip().startswith('[')),
    len(lines)
  )
  setting_index = next(
    (index for index in range(script_info_index + 1, section_end_index) if re.match(r'\s*ScaledBorderAndShadow\s*:', lines[index], flags=re.IGNORECASE)),
    None
  )

  if setting_index is None:
    lines.insert(script_info_index + 1, f'ScaledBorderAndShadow: no{line_ending}')
  else:
    original_line = lines[setting_index]
    ending = '\r\n' if original_line.endswith('\r\n') else '\n' if original_line.endswith('\n') else ''
    setting_name = original_line.split(':', 1)[0].strip()
    indentation = original_line[:len(original_line) - len(original_line.lstrip())]
    lines[setting_index] = f'{indentation}{setting_name}: no{ending}'

  return ''.join(lines)

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
  lookup_colors: list[str] | None = None,
):
  field_index = field_indices.get(field_name)
  condition_index = field_indices.get(condition_field_name) if condition_field_name else None
  if field_index is None or (condition_field_name is not None and condition_index is None):
    return match.group(0)

  fields = match.group(1).split(',')
  if len(fields) <= max(field_index, condition_index or 0):
    return match.group(0)
  if condition_index is None or float(fields[condition_index]) > 0:
    if lookup_colors is not None and not any(
      re.search(rf'{HEX_DIGIT_PATTERN}{{0,2}}{lookup_color[4:6]}{lookup_color[2:4]}{lookup_color[0:2]}$', fields[field_index], flags=re.IGNORECASE)
      for lookup_color in lookup_colors
    ):
      return match.group(0)
    if len(replacement_color) == 8:
      fields[field_index] = re.sub(rf'(?<=&H){HEX_DIGIT_PATTERN}{{8}}', replacement_color, fields[field_index])
    else:
      fields[field_index] = re.sub(HEX_COLOUR_VALUE_PATTERN, replacement_color, fields[field_index])
  return 'Style: ' + ','.join(fields)

def replace_ass_style_field(
  match: re.Match,
  field_indices: dict[str, int],
  field_name: str,
  replacement_value: str,
  lookup_values: list[str] | None = None,
):
  field_index = field_indices.get(field_name)
  if field_index is None:
    return match.group(0)

  fields = match.group(1).split(',')
  if len(fields) <= field_index:
    return match.group(0)
  if lookup_values is not None and not any(
    fields[field_index].strip().casefold() == lookup_value.strip().casefold()
    for lookup_value in lookup_values
  ):
    return match.group(0)
  fields[field_index] = replacement_value
  return 'Style: ' + ','.join(fields)

import re

from _constants import ASS_SUBTITLE_EXTS, VTT_EXT


ASS_LOSSY_TAG_PATTERN = re.compile(
  r'\\(?:pos\(|move\(|org\(|a[1-9]|clip\(|iclip\(|p[1-9]\d*)',
  re.IGNORECASE,
)
VTT_LOSSY_SETTING_PATTERN = re.compile(
  r'(?:^|\s)(?:line|position|size|align|vertical):\S+',
  re.IGNORECASE,
)


def has_srt_incompatible_data(
  file_path: str,
  ext: str,
) -> bool:
  with open(file_path, encoding='utf-8-sig', errors='replace') as input_file:
    lines = input_file.read().splitlines()

  if ext in ASS_SUBTITLE_EXTS:
    return has_srt_incompatible_ass_data(lines)
  if ext == VTT_EXT:
    return has_srt_incompatible_vtt_data(lines)
  return False


def has_srt_incompatible_ass_data(
  lines: list[str],
) -> bool:
  section = ''
  format_fields = []
  lossy_styles = set()
  used_styles = set()

  for line in lines:
    stripped_line = line.strip()
    if stripped_line.startswith('[') and stripped_line.endswith(']'):
      section = stripped_line[1:-1].casefold()
      format_fields = []
      continue

    key, separator, value = stripped_line.partition(':')
    if not separator:
      continue
    key = key.casefold()
    value = value.strip()

    if key == 'format' and section in {'v4 styles', 'v4+ styles', 'events'}:
      format_fields = [field.strip().casefold() for field in value.split(',')]
    elif key == 'style' and section in {'v4 styles', 'v4+ styles'}:
      fields = value.split(',', max(0, len(format_fields) - 1))
      if len(fields) != len(format_fields):
        continue
      style = dict(zip(format_fields, fields))
      colour = re.fullmatch(
        r'(?:&H)?([0-9A-F]{2})?([0-9A-F]{6})',
        style.get('backcolour', '').strip(),
        re.IGNORECASE,
      )
      if (
        style.get('borderstyle', '').strip() == '3'
        and colour
        and colour[1] != 'FF'
      ):
        lossy_styles.add(style.get('name', '').strip().casefold())
    elif key == 'dialogue' and section == 'events':
      fields = value.split(',', max(0, len(format_fields) - 1))
      if len(fields) != len(format_fields):
        continue
      dialogue = dict(zip(format_fields, fields))
      used_styles.add(dialogue.get('style', '').strip().casefold())
      if ASS_LOSSY_TAG_PATTERN.search(dialogue.get('text', '')):
        return True
      if dialogue.get('effect', '').strip() or any(
        dialogue.get(margin, '').strip().lstrip('0')
        for margin in ('marginl', 'marginr', 'marginv')
      ):
        return True

  return bool(lossy_styles & used_styles)


def has_srt_incompatible_vtt_data(
  lines: list[str],
) -> bool:
  in_style_block = False
  for line in lines:
    stripped_line = line.strip()
    if stripped_line == 'STYLE':
      in_style_block = True
      continue
    if not stripped_line:
      in_style_block = False
      continue
    if '-->' in line and VTT_LOSSY_SETTING_PATTERN.search(
      line.split('-->', 1)[1]
    ):
      return True
    if in_style_block and re.search(
      r'\bbackground(?:-color)?\s*:', line, re.IGNORECASE
    ):
      return True
  return False

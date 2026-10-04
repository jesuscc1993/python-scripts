import os
import re

from functools import partial
from mtlogger import logger
from mtfs import read_text_file, write_text_file
from mtprompt import Prompt

from _constants import ASS_SUBTITLE_EXTS, VTT_EXT

SRT_TIME_PATTERN = r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})'
VTT_TIME_PATTERN = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})'
ASS_TIME_PATTERN = r'(\d+,)(\d+:\d{2}:\d{2}\.\d{2}),(\d+:\d{2}:\d{2}\.\d{2})'

def main():
  subs_file = Prompt.file(
    'Enter the path to the subtitles file'
  )
  shift = Prompt.int(
    'Enter milliseconds to shift (+/-)'
  )

  shift_subtitles(subs_file, shift)

def parse_time(
  time_str: str,
):
  parts = time_str.replace(',', '.').split(':')
  hours = int(parts[0])
  minutes = int(parts[1])
  seconds = float(parts[2])
  total_ms = int((hours * 3600 + minutes * 60 + seconds) * 1000)
  return total_ms

def get_time_units(
  ms: int,
):
  ms = max(0, ms)
  hours, remainder = divmod(ms, 3600000)
  minutes, remainder = divmod(remainder, 60000)
  seconds, milliseconds = divmod(remainder, 1000)
  return hours, minutes, seconds, milliseconds

def ms_to_srt_time(
  ms: int,
):
  hours, minutes, seconds, milliseconds = get_time_units(ms)
  return f'{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}'

def ms_to_vtt_time(
  ms: int,
):
  hours, minutes, seconds, milliseconds = get_time_units(ms)
  return f'{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}'

def ms_to_ass_time(
  ms: int,
):
  rounded_ms = round(ms / 10) * 10
  hours, minutes, seconds, milliseconds = get_time_units(rounded_ms)
  return f'{hours:01d}:{minutes:02d}:{seconds:02d}.{milliseconds // 10:02d}'

def replace_srt_time(
  match: re.Match,
  ms_to_shift: int,
):
  start_time = parse_time(match.group(1))
  end_time = parse_time(match.group(2))
  return f'{ms_to_srt_time(start_time + ms_to_shift)} --> {ms_to_srt_time(end_time + ms_to_shift)}'

def replace_vtt_time(
  match: re.Match,
  ms_to_shift: int,
):
  start_time = parse_time(match.group(1))
  end_time = parse_time(match.group(2))
  return f'{ms_to_vtt_time(start_time + ms_to_shift)} --> {ms_to_vtt_time(end_time + ms_to_shift)}'

def replace_ass_time(
  match: re.Match,
  ms_to_shift: int,
):
  start_time = parse_time(match.group(2))
  end_time = parse_time(match.group(3))
  return f'{match.group(1)}{ms_to_ass_time(start_time + ms_to_shift)},{ms_to_ass_time(end_time + ms_to_shift)}'

def shift_subtitles(
  subs_path: str,
  ms_to_shift: int,
):
  content = read_text_file(subs_path)
  ext = os.path.splitext(subs_path)[1].lower()

  if ext in ASS_SUBTITLE_EXTS:
    new_content = re.sub(ASS_TIME_PATTERN, partial(replace_ass_time, ms_to_shift=ms_to_shift), content)
  elif ext == VTT_EXT:
    new_content = re.sub(VTT_TIME_PATTERN, partial(replace_vtt_time, ms_to_shift=ms_to_shift), content)
  else:
    new_content = re.sub(SRT_TIME_PATTERN, partial(replace_srt_time, ms_to_shift=ms_to_shift), content)

  write_text_file(subs_path, new_content)

  logger.success(
    f'Subtitles shifted by {ms_to_shift}ms',
    prefix_newline=True
  )

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

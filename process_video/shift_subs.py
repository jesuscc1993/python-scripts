import re

from functools import partial
from mtlogger import logger
from mtfs import read_text_file, write_text_file
from mtprompt import Prompt

def main():
  srt_file = Prompt.file(
    'Enter the path to an SRT file'
  )
  shift = Prompt.int(
    'Enter milliseconds to shift (+/-)'
  )

  shift_subtitles(srt_file, shift)

def parse_time(
  time_str: str,
):
  parts = time_str.replace(',', '.').split(':')
  hours = int(parts[0])
  minutes = int(parts[1])
  seconds = float(parts[2])
  total_ms = int((hours * 3600 + minutes * 60 + seconds) * 1000)
  return total_ms

def ms_to_time(
  ms: int,
):
  ms = max(0, ms)
  hours, remainder = divmod(ms, 3600000)
  minutes, remainder = divmod(remainder, 60000)
  seconds, milliseconds = divmod(remainder, 1000)
  return f'{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}'

def replace_time(
  match: re.Match,
  ms_to_shift: int,
):
  start_time = parse_time(match.group(1))
  end_time = parse_time(match.group(2))
  return f'{ms_to_time(start_time + ms_to_shift)} --> {ms_to_time(end_time + ms_to_shift)}'

def shift_subtitles(
  srt_path: str,
  ms_to_shift: int,
):
  content = read_text_file(srt_path)
  time_pattern = r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})'
  new_content = re.sub(time_pattern, partial(replace_time, ms_to_shift=ms_to_shift), content)
  write_text_file(srt_path, new_content)

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

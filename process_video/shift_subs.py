import re

from functools import partial
from mtlogger import logger
from mtprompt import Prompt

from _common import prompt_path

def main():
  srt_file = prompt_path('Enter the path to an SRT file:\n')

  try:
    shift = int(input('Enter milliseconds to shift (*/-):\n'))
  except ValueError:
    logger.error('\nPlease enter a valid integer')
    return

  shift_subtitles(srt_file, shift)

def parse_time(time_str):
  parts = time_str.replace(',', '.').split(':')
  hours = int(parts[0])
  minutes = int(parts[1])
  seconds = float(parts[2])
  total_ms = int((hours * 3600 + minutes * 60 + seconds) * 1000)
  return total_ms

def ms_to_time(ms):
  ms = max(0, ms)
  hours, remainder = divmod(ms, 3600000)
  minutes, remainder = divmod(remainder, 60000)
  seconds, milliseconds = divmod(remainder, 1000)
  return f'{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}'

def replace_time(match, ms_to_shift):
  start_time = parse_time(match.group(1))
  end_time = parse_time(match.group(2))
  return f'{ms_to_time(start_time + ms_to_shift)} --> {ms_to_time(end_time + ms_to_shift)}'

def shift_subtitles(srt_path, ms_to_shift):
  with open(srt_path, 'r', encoding='utf-8') as f:
    content = f.read()

  time_pattern = r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})'

  new_content = re.sub(time_pattern, partial(replace_time, ms_to_shift=ms_to_shift), content)

  with open(srt_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

  logger.success(f'\nSubtitles shifted by {ms_to_shift}ms')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)
  Prompt.enterToExit()

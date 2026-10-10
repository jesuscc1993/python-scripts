import os
import re
import subprocess

from mtfs import read_text_file, write_text_file

from _common_ass import post_process_ass_subtitles
from _common_html import post_process_html_subtitles
from _constants import ASS_SUBTITLE_EXTS, ENCODING, SUBTITLE_EXTS_WITH_HTML_TAGS

def add_missing_spaces_to_subs_file(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)
  content = re.sub(r'(?<=[a-záéíóúüñ])([.,;:!?]+)([A-ZÁÉÍÓÚÜÑ])', r'\1 \2', content)
  content = re.sub(r'(?<=\S)(\.\.\.)(?=[A-ZÁÉÍÓÚÜÑ])', r'\1 ', content)

  write_text_file(file_path, content, ENCODING)

def fix_invalid_chars_in_subs_file(
  file_path: str,
):
  content = read_text_file(file_path, ENCODING)
  content = content.replace('\u00ce\u00bd', 'v').replace('\u00ce\u009d', 'V')
  write_text_file(file_path, content, ENCODING)

def post_process_subs_file(
  file_path: str,
  ext: str,
):
  if ext in SUBTITLE_EXTS_WITH_HTML_TAGS:
    post_process_html_subtitles(file_path)
  elif ext in ASS_SUBTITLE_EXTS:
    post_process_ass_subtitles(file_path)

def get_ext(
  file_path: str,
):
  return os.path.splitext(file_path)[1].lower()

def generate_tmp_dir(
  dir_path: str,
):
  tmp_dir = os.path.join(dir_path, '.tmp')
  os.makedirs(tmp_dir, exist_ok=True)
  subprocess.run(['attrib', '+H', tmp_dir], check=False, capture_output=True)
  return tmp_dir

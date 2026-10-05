import sys
import os
import tempfile
import unittest

from mtfs import read_text_file, write_text_file
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _common import add_missing_spaces_to_subs_file, fix_invalid_chars_in_subs_file, post_process_subs_file, ENCODING
from _settings import SETTINGS

def process(func, content, *args):
  fd, path = tempfile.mkstemp()
  os.close(fd)
  try:
    write_text_file(path, content, ENCODING)
    func(path, *args)
    return read_text_file(path, ENCODING)
  finally:
    os.remove(path)

class TestAddMissingSpacesPunctuation(unittest.TestCase):
  def test_inserts_space_between_punctuation_and_uppercase(self):
    self.assertEqual(process(add_missing_spaces_to_subs_file, 'foo.Bar'), 'foo. Bar')

  def test_keeps_unchanged_when_punctuation_followed_by_lowercase(self):
    self.assertEqual(process(add_missing_spaces_to_subs_file, 'foo.bar'), 'foo.bar')

  def test_keeps_unchanged_when_punctuation_already_spaced(self):
    self.assertEqual(process(add_missing_spaces_to_subs_file, 'foo. Bar'), 'foo. Bar')

class TestAddMissingSpacesEllipsis(unittest.TestCase):
  def test_inserts_space_when_ellipsis_attached_and_followed_by_uppercase(self):
    self.assertEqual(process(add_missing_spaces_to_subs_file, 'foo...Bar'), 'foo... Bar')

  def test_keeps_unchanged_when_ellipsis_attached_but_followed_by_lowercase(self):
    self.assertEqual(process(add_missing_spaces_to_subs_file, 'foo...bar'), 'foo...bar')

  def test_keeps_unchanged_when_ellipsis_at_start_of_string(self):
    self.assertEqual(process(add_missing_spaces_to_subs_file, '...bar'), '...bar')

  def test_keeps_unchanged_when_ellipsis_preceded_by_space(self):
    self.assertEqual(process(add_missing_spaces_to_subs_file, 'foo ...bar'), 'foo ...bar')

  def test_keeps_unchanged_when_ellipsis_already_spaced(self):
    self.assertEqual(process(add_missing_spaces_to_subs_file, 'foo... bar'), 'foo... bar')

class TestFixInvalidCharsInSubsFile(unittest.TestCase):
  def test_replaces_invalid_greek_characters(self):
    self.assertEqual(process(fix_invalid_chars_in_subs_file, '\u00ce\u009di\u00ce\u00bdid'), 'Vivid')

class TestPostProcessSubsFile(unittest.TestCase):
  def test_strips_html_tags_for_srt_ext_when_strip_tags_enabled(self):
    with patch.dict(SETTINGS, { 'replace_color': False }), patch.dict(SETTINGS['strip_settings'], { 'enabled': True }):
      result = process(post_process_subs_file, '<font color="#FFFFFF">Hi</font>', '.srt')
    self.assertEqual(result, 'Hi')

  def test_keeps_html_tags_for_srt_ext_when_strip_tags_disabled(self):
    with patch.dict(SETTINGS, { 'replace_color': False }), patch.dict(SETTINGS['strip_settings'], { 'enabled': False }):
      result = process(post_process_subs_file, '<font color="#FFFFFF">Hi</font>', '.srt')
    self.assertEqual(result, '<font color="#FFFFFF">Hi</font>')

  def test_replaces_white_font_color_for_srt_ext_when_replace_color_enabled(self):
    with patch.dict(SETTINGS, { 'replace_color': True }), patch.dict(SETTINGS['strip_settings'], { 'enabled': False }):
      result = process(post_process_subs_file, '<font color="#FFFFFF">Hi</font>', '.srt')
    self.assertEqual(result, '<font color="#FFFF55">Hi</font>')

  def test_keeps_white_font_color_for_srt_ext_when_replace_color_disabled(self):
    with patch.dict(SETTINGS, { 'replace_color': False }), patch.dict(SETTINGS['strip_settings'], { 'enabled': False }):
      result = process(post_process_subs_file, '<font color="#FFFFFF">Hi</font>', '.srt')
    self.assertEqual(result, '<font color="#FFFFFF">Hi</font>')

  def test_skips_replace_color_when_strip_settings_color_enabled(self):
    with patch.dict(SETTINGS, { 'replace_color': True }), patch.dict(SETTINGS['strip_settings'], { 'enabled': False, 'color': True }):
      result = process(post_process_subs_file, '<font color="#FFFFFF">Hi</font>', '.srt')
    self.assertEqual(result, '<font color="#FFFFFF">Hi</font>')

  def test_runs_ass_post_processing_for_ass_ext(self):
    content = r'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\c&HFFFFFF&}Hello'
    with patch.dict(SETTINGS, { 'replace_color': True, 'force_border_color': False, 'force_text_color': False }):
      result = process(post_process_subs_file, content, '.ass')
    self.assertIn(r'{\c&H55FFFF&}', result)

  def test_ignores_unsupported_ext(self):
    content = '<font color="#FFFFFF">Hi</font>'
    result = process(post_process_subs_file, content, '.txt')
    self.assertEqual(result, content)

if __name__ == '__main__':
  unittest.main()

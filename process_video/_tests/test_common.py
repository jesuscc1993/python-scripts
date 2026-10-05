import sys
import os
import tempfile
import unittest

from mtfs import read_text_file, write_text_file
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _common import add_missing_spaces_to_subs_file, fix_invalid_chars_in_subs_file, post_process_subs_file, strip_tags_from_subs_file, strip_attribute, STRIP_SETTINGS, ENCODING

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

class TestStripTagsFromSubsFile(unittest.TestCase):
  def test_removes_entire_font_tags_when_fonts_setting_enabled(self):
    result = process(strip_tags_from_subs_file, '<font color="#FFFFFF">Hello</font>')
    self.assertEqual(result, 'Hello')

  def test_removes_only_configured_attribute_when_fonts_setting_disabled(self):
    with patch.dict(STRIP_SETTINGS, { 'fonts': False, 'color': True }):
      result = process(strip_tags_from_subs_file, '<font color="red" size="1">Hi</font>')
    self.assertEqual(result, '<font size="1">Hi</font>')

class TestFixInvalidCharsInSubsFile(unittest.TestCase):
  def test_replaces_invalid_greek_characters(self):
    self.assertEqual(process(fix_invalid_chars_in_subs_file, '\u00ce\u009di\u00ce\u00bdid'), 'Vivid')

class TestStripAttribute(unittest.TestCase):
  def test_removes_matching_attribute(self):
    self.assertEqual(strip_attribute('<font color="red" size="1">', 'color'), '<font size="1">')

  def test_keeps_unchanged_when_attribute_not_present(self):
    self.assertEqual(strip_attribute('<font size="1">', 'color'), '<font size="1">')

class TestPostProcessSubsFile(unittest.TestCase):
  def test_strips_html_tags_for_srt_ext_when_strip_tags_enabled(self):
    with patch('_common.STRIP_TAGS', True):
      result = process(post_process_subs_file, '<font color="#FFFFFF">Hi</font>', '.srt')
    self.assertEqual(result, 'Hi')

  def test_keeps_html_tags_for_srt_ext_when_strip_tags_disabled(self):
    with patch('_common.STRIP_TAGS', False):
      result = process(post_process_subs_file, '<font color="#FFFFFF">Hi</font>', '.srt')
    self.assertEqual(result, '<font color="#FFFFFF">Hi</font>')

  def test_runs_ass_post_processing_for_ass_ext(self):
    content = r'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\c&HFFFFFF&}Hello'
    with patch('_ass_common.REPLACE_COLOR', True), patch('_ass_common.FORCE_BORDER_COLOR', False), patch('_ass_common.FORCE_TEXT_COLOR', False):
      result = process(post_process_subs_file, content, '.ass')
    self.assertIn(r'{\c&H55FFFF&}', result)

  def test_ignores_unsupported_ext(self):
    content = '<font color="#FFFFFF">Hi</font>'
    result = process(post_process_subs_file, content, '.txt')
    self.assertEqual(result, content)

if __name__ == '__main__':
  unittest.main()

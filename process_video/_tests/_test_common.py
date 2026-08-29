import sys
import os
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _common import add_missing_spaces, strip_tags_from_subs_file, strip_attribute, STRIP_SETTINGS, ENCODING

def process(func, content):
  fd, path = tempfile.mkstemp()
  os.close(fd)
  try:
    with open(path, 'w', encoding = ENCODING) as f:
      f.write(content)
    func(path)
    with open(path, 'r', encoding = ENCODING) as f:
      return f.read()
  finally:
    os.remove(path)

class TestAddMissingSpacesPunctuation(unittest.TestCase):
  def test_inserts_space_between_punctuation_and_uppercase(self):
    self.assertEqual(process(add_missing_spaces, 'foo.Bar'), 'foo. Bar')

  def test_keeps_unchanged_when_punctuation_followed_by_lowercase(self):
    self.assertEqual(process(add_missing_spaces, 'foo.bar'), 'foo.bar')

  def test_keeps_unchanged_when_punctuation_already_spaced(self):
    self.assertEqual(process(add_missing_spaces, 'foo. Bar'), 'foo. Bar')

class TestAddMissingSpacesEllipsis(unittest.TestCase):
  def test_inserts_space_when_ellipsis_attached_and_followed_by_uppercase(self):
    self.assertEqual(process(add_missing_spaces, 'foo...Bar'), 'foo... Bar')

  def test_keeps_unchanged_when_ellipsis_attached_but_followed_by_lowercase(self):
    self.assertEqual(process(add_missing_spaces, 'foo...bar'), 'foo...bar')

  def test_keeps_unchanged_when_ellipsis_at_start_of_string(self):
    self.assertEqual(process(add_missing_spaces, '...bar'), '...bar')

  def test_keeps_unchanged_when_ellipsis_preceded_by_space(self):
    self.assertEqual(process(add_missing_spaces, 'foo ...bar'), 'foo ...bar')

  def test_keeps_unchanged_when_ellipsis_already_spaced(self):
    self.assertEqual(process(add_missing_spaces, 'foo... bar'), 'foo... bar')

class TestStripTagsFromSubsFile(unittest.TestCase):
  def test_removes_entire_font_tags_when_fonts_setting_enabled(self):
    result = process(strip_tags_from_subs_file, '<font color="#FFFFFF">Hello</font>')
    self.assertEqual(result, 'Hello')

  def test_removes_only_configured_attribute_when_fonts_setting_disabled(self):
    with patch.dict(STRIP_SETTINGS, { 'fonts': False, 'color': True }):
      result = process(strip_tags_from_subs_file, '<font color="red" size="1">Hi</font>')
    self.assertEqual(result, '<font size="1">Hi</font>')

class TestStripAttribute(unittest.TestCase):
  def test_removes_matching_attribute(self):
    self.assertEqual(strip_attribute('<font color="red" size="1">', 'color'), '<font size="1">')

  def test_keeps_unchanged_when_attribute_not_present(self):
    self.assertEqual(strip_attribute('<font size="1">', 'color'), '<font size="1">')

if __name__ == '__main__':
  unittest.main()

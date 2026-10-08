import sys
import os
import tempfile
import unittest

from mtfs import read_text_file, write_text_file
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _common_html import post_process_html_subtitles, replace_html_text_color, force_html_font, strip_conversion_leftovers, strip_html_tags, strip_attribute, strip_unsupported_tags
from _constants import ENCODING
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

class TestStripHtmlTags(unittest.TestCase):
  def test_removes_entire_font_tags_when_fonts_setting_enabled(self):
    self.assertEqual(strip_html_tags('<font color="#FFFFFF">Hello</font>'), 'Hello')

  def test_removes_only_configured_attribute_when_fonts_setting_disabled(self):
    with patch.dict(SETTINGS['strip_settings'], { 'fonts': False, 'color': True }):
      result = strip_html_tags('<font color="red" size="1">Hi</font>')
    self.assertEqual(result, '<font size="1">Hi</font>')

  def test_removes_span_tags_but_keeps_supported_tags(self):
    result = strip_html_tags('<i>No.</i><span style="style2"> </i><i>Nada.</i>')
    self.assertEqual(result, '<i>No.</i> </i><i>Nada.</i>')

class TestStripConversionLeftovers(unittest.TestCase):
  def test_removes_ass_alignment_overrides(self):
    result = strip_conversion_leftovers(r'{\an7}Top left\N{\an9}Top right')
    self.assertEqual(result, r'Top left\NTop right')

  def test_keeps_text_and_non_alignment_braces(self):
    content = 'Text {not an override} and {\\an0}'
    self.assertEqual(strip_conversion_leftovers(content), content)

class TestStripUnsupportedTags(unittest.TestCase):
  def test_removes_span_tags(self):
    self.assertEqual(strip_unsupported_tags('<span style="style2">foo</span>'), 'foo')

  def test_keeps_supported_tags(self):
    self.assertEqual(strip_unsupported_tags('<b>foo</b><i>bar</i><u>baz</u><s>qux</s>'), '<b>foo</b><i>bar</i><u>baz</u><s>qux</s>')

  def test_keeps_font_tags(self):
    self.assertEqual(strip_unsupported_tags('<font color="red">foo</font>'), '<font color="red">foo</font>')

class TestReplaceHtmlTextColor(unittest.TestCase):
  def test_replaces_white_color_with_hash_prefix(self):
    self.assertEqual(replace_html_text_color('<font color="#FFFFFF">Hi</font>'), '<font color="#FFFF55">Hi</font>')

  def test_replaces_white_color_without_hash_prefix(self):
    self.assertEqual(replace_html_text_color('<font color="FFFFFF">Hi</font>'), '<font color="#FFFF55">Hi</font>')

  def test_keeps_unchanged_when_color_is_not_white(self):
    self.assertEqual(replace_html_text_color('<font color="#123456">Hi</font>'), '<font color="#123456">Hi</font>')

class TestStripAttribute(unittest.TestCase):
  def test_removes_matching_attribute(self):
    self.assertEqual(strip_attribute('<font color="red" size="1">', 'color'), '<font size="1">')

  def test_keeps_unchanged_when_attribute_not_present(self):
    self.assertEqual(strip_attribute('<font size="1">', 'color'), '<font size="1">')

class TestForceHtmlFont(unittest.TestCase):
  def test_replaces_existing_face_attribute(self):
    with patch.dict(SETTINGS, { 'preferred_font': 'Quicksand SemiBold' }):
      result = force_html_font('<font face="Arial">Hi</font>')
    self.assertEqual(result, '<font face="Quicksand SemiBold">Hi</font>')

  def test_inserts_face_attribute_when_missing(self):
    with patch.dict(SETTINGS, { 'preferred_font': 'Quicksand SemiBold' }):
      result = force_html_font('<font color="red">Hi</font>')
    self.assertEqual(result, '<font color="red" face="Quicksand SemiBold">Hi</font>')

class TestPostProcessHtmlSubtitles(unittest.TestCase):
  def test_strips_tags_and_replaces_color_in_one_pass(self):
    with patch.dict(SETTINGS, { 'replace_color': True }), patch.dict(SETTINGS['strip_settings'], { 'enabled': False }):
      result = process(post_process_html_subtitles, '<font color="#FFFFFF">Hi</font>')
    self.assertEqual(result, '<font color="#FFFF55">Hi</font>')

  def test_forces_font_when_fonts_setting_disabled(self):
    with patch.dict(SETTINGS, { 'force_font': True, 'preferred_font': 'Quicksand SemiBold' }), patch.dict(SETTINGS['strip_settings'], { 'enabled': False, 'fonts': False }):
      result = process(post_process_html_subtitles, '<font face="Arial">Hi</font>')
    self.assertEqual(result, '<font face="Quicksand SemiBold">Hi</font>')

  def test_does_not_force_font_when_fonts_setting_enabled(self):
    with patch.dict(SETTINGS, { 'force_font': True, 'preferred_font': 'Quicksand SemiBold' }), patch.dict(SETTINGS['strip_settings'], { 'enabled': False, 'fonts': True }):
      result = process(post_process_html_subtitles, '<font face="Arial">Hi</font>')
    self.assertEqual(result, '<font face="Arial">Hi</font>')

if __name__ == '__main__':
  unittest.main()

if __name__ == '__main__':
  unittest.main()

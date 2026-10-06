import sys
import os
import tempfile
import unittest

from mtfs import read_text_file, write_text_file
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _common_html import post_process_html_subtitles, replace_html_text_color, strip_html_tags, strip_attribute, strip_unsupported_tags
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

class TestPostProcessHtmlSubtitles(unittest.TestCase):
  def test_strips_tags_and_replaces_color_in_one_pass(self):
    with patch.dict(SETTINGS, { 'replace_color': True }), patch.dict(SETTINGS['strip_settings'], { 'enabled': False }):
      result = process(post_process_html_subtitles, '<font color="#FFFFFF">Hi</font>')
    self.assertEqual(result, '<font color="#FFFF55">Hi</font>')

if __name__ == '__main__':
  unittest.main()

if __name__ == '__main__':
  unittest.main()

import sys
import os
import tempfile
import unittest

from mtfs import read_text_file, write_text_file
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _common_ass import post_process_ass_subtitles, rgb_to_bgr
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

class TestPostProcessAssFile(unittest.TestCase):
  def test_replaces_white_color_when_replace_color_enabled(self):
    content = r'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\c&HFFFFFF&}Hello'
    with patch.dict(SETTINGS, { 'replace_color': True, 'force_border_color': False, 'force_text_color': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn(r'{\c&H55FFFF&}', result)

  def test_keeps_white_color_when_replace_color_disabled(self):
    content = r'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\c&HFFFFFF&}Hello'
    with patch.dict(SETTINGS, { 'replace_color': False, 'force_border_color': False, 'force_text_color': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn(r'{\c&HFFFFFF&}', result)

  def test_forces_border_color_only_when_outline_width_positive(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: WithBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
      'Style: NoBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_color': False, 'force_border_color': True, 'force_text_color': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('WithBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00000000', result)
    self.assertIn('NoBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00445566', result)

  def test_does_not_force_border_color_when_disabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: WithBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_color': False, 'force_border_color': False, 'force_text_color': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('&H00445566', result)

  def test_forces_text_color_unconditionally_when_enabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00112233,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_color': False, 'force_border_color': False, 'force_text_color': True }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('&H0055FFFF', result)

  def test_does_not_force_text_color_when_disabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00112233,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_color': False, 'force_border_color': False, 'force_text_color': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('&H00112233', result)

  def test_skips_force_colors_when_format_line_is_missing(self):
    content = 'Style: Default,Arial,20,&H00112233,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    with patch.dict(SETTINGS, { 'replace_color': False, 'force_border_color': True, 'force_text_color': True }):
      result = process(post_process_ass_subtitles, content)
    self.assertEqual(result, content)

class TestRgbToBgr(unittest.TestCase):
  def test_reverses_byte_order(self):
    self.assertEqual(rgb_to_bgr('FFFF55'), '55FFFF')

  def test_keeps_symmetric_colors_unchanged(self):
    self.assertEqual(rgb_to_bgr('FFFFFF'), 'FFFFFF')
    self.assertEqual(rgb_to_bgr('000000'), '000000')

if __name__ == '__main__':
  unittest.main()

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
  def test_replaces_white_color_when_replace_foreground_color_enabled(self):
    content = r'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\c&HFFFFFF&}Hello'
    with patch.dict(SETTINGS, { 'replace_foreground_color': True, 'force_border_color': False, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn(r'{\c&H55FFFF&}', result)

  def test_keeps_white_color_when_replace_foreground_color_disabled(self):
    content = r'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\c&HFFFFFF&}Hello'
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'force_border_color': False, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn(r'{\c&HFFFFFF&}', result)

  def test_replaces_multiple_foreground_colors_when_enabled(self):
    content = r'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\c&HFFFFFF&}foo{\c&H332211&}bar'
    with patch.dict(SETTINGS, { 'replace_foreground_color': True, 'lookup_foreground_colors': ['FFFFFF', '112233'], 'force_border_color': False, 'force_foreground_color': False, 'force_outline_thickness_and_shadow_offset': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertEqual(result, r'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\c&H55FFFF&}foo{\c&H55FFFF&}bar')

  def test_replaces_border_color_when_enabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'replace_border_color': True, 'lookup_border_colors': ['665544'], 'preferred_border_color': '000000', 'force_border_color': False, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('&H00000000', result)

  def test_replaces_background_color_when_enabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00400000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'replace_border_color': False, 'replace_background_color': True, 'lookup_background_colors': ['000040'], 'preferred_background_color': 'AABBCC', 'force_border_color': False, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('&H00445566,&H00CCBBAA', result)

  def test_forces_background_color_when_enabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00112233,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'replace_border_color': False, 'replace_background_color': False, 'force_background_color': True, 'preferred_background_color': 'AABBCC', 'force_border_color': False, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('&H00445566,&H00CCBBAA', result)

  def test_replaces_font_only_for_lookup_values(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Matched,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
      'Style: Unmatched,Times New Roman,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'replace_border_color': False, 'replace_background_color': False, 'replace_font': True, 'lookup_fonts': ['Arial'], 'preferred_font': 'Quicksand', 'force_font': False, 'force_border_color': False, 'force_foreground_color': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('Style: Matched,Quicksand,20,', result)
    self.assertIn('Style: Unmatched,Times New Roman,20,', result)

  def test_forces_border_color_only_when_outline_width_positive(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: WithBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
      'Style: NoBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'force_border_color': True, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('WithBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00000000', result)
    self.assertIn('NoBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00445566', result)

  def test_does_not_force_border_color_when_disabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: WithBorder,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'force_border_color': False, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('&H00445566', result)

  def test_forces_outline_thickness_and_shadow_offset_and_disables_scaling(self):
    content = (
      '[Script Info]\n'
      'ScaledBorderAndShadow: yes\n'
      '\n'
      '[V4+ Styles]\n'
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,4,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'replace_border_color': False, 'replace_background_color': False, 'force_border_color': False, 'force_outline_thickness_and_shadow_offset': True, 'preferred_outline_thickness': '2', 'preferred_shadow_offset': '4', 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('ScaledBorderAndShadow: no', result)
    self.assertIn('1,2,4,8,', result)

  def test_does_not_change_outline_shadow_or_scaling_when_disabled(self):
    content = (
      '[Script Info]\n'
      'ScaledBorderAndShadow: yes\n'
      '\n'
      '[V4+ Styles]\n'
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,4,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'replace_border_color': False, 'replace_background_color': False, 'force_border_color': False, 'force_outline_thickness_and_shadow_offset': False, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertEqual(result, content)

  def test_adds_script_info_scaling_setting_when_missing(self):
    content = (
      '[V4+ Styles]\n'
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00112233,&H000000FF,&H00445566,&H00112233,0,0,0,0,100,100,0,0,1,4,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'replace_border_color': False, 'replace_background_color': False, 'force_border_color': False, 'force_outline_thickness_and_shadow_offset': True, 'preferred_outline_thickness': '2', 'preferred_shadow_offset': '4', 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertTrue(result.startswith('[Script Info]\nScaledBorderAndShadow: no\n\n[V4+ Styles]'))

  def test_forces_foreground_color_unconditionally_when_enabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00112233,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'force_border_color': False, 'force_foreground_color': True, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('&H0055FFFF', result)

  def test_does_not_force_foreground_color_when_disabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00112233,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'force_border_color': False, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('&H00112233', result)

  def test_skips_force_colors_when_format_line_is_missing(self):
    content = 'Style: Default,Arial,20,&H00112233,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'force_border_color': True, 'force_foreground_color': True, 'force_outline_thickness_and_shadow_offset': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertEqual(result, content)

  def test_forces_font_unconditionally_when_enabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00112233,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'force_border_color': False, 'force_foreground_color': False, 'force_font': True, 'preferred_font': 'Quicksand SemiBold' }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('Style: Default,Quicksand SemiBold,20,', result)

  def test_does_not_force_font_when_disabled(self):
    content = (
      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: Default,Arial,20,&H00112233,&H000000FF,&H00445566,&H00000000,0,0,0,0,100,100,0,0,1,2,1,8,10,10,20,1\n'
    )
    with patch.dict(SETTINGS, { 'replace_foreground_color': False, 'force_border_color': False, 'force_foreground_color': False, 'force_font': False }):
      result = process(post_process_ass_subtitles, content)
    self.assertIn('Style: Default,Arial,20,', result)

class TestRgbToBgr(unittest.TestCase):
  def test_reverses_byte_order(self):
    self.assertEqual(rgb_to_bgr('FFFF55'), '55FFFF')

  def test_keeps_symmetric_colors_unchanged(self):
    self.assertEqual(rgb_to_bgr('FFFFFF'), 'FFFFFF')
    self.assertEqual(rgb_to_bgr('000000'), '000000')

if __name__ == '__main__':
  unittest.main()

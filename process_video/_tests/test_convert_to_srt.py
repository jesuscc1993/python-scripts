import os
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from convert_to_srt import convert_to_srt, process_file


class TestConvertToSrt(unittest.TestCase):
  def setUp(self):
    self.dir_path = os.path.join(
      tempfile.gettempdir(),
      'python-scripts-tests',
      'process_video',
      'convert_to_srt',
      self._testMethodName,
    )
    shutil.rmtree(self.dir_path, ignore_errors=True)
    os.makedirs(self.dir_path)

  def tearDown(self):
    shutil.rmtree(self.dir_path, ignore_errors=True)

  def test_converts_subtitle_and_moves_source_to_trash(self):
    input_path = os.path.join(self.dir_path, 'foo.vtt')
    output_path = os.path.join(self.dir_path, 'foo.srt')
    with open(input_path, 'w', encoding='utf-8') as input_file:
      input_file.write('WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nfoo\n')

    def run_ffmpeg(command, **kwargs):
      with open(command[-1], 'w', encoding='utf-8') as output_file:
        output_file.write('1\n00:00:00,000 --> 00:00:01,000\nfoo\n')
      return SimpleNamespace(returncode=0, stderr='')

    with (
      patch('convert_to_srt.subprocess.run', side_effect=run_ffmpeg) as run,
      patch('convert_to_srt.send2trash') as trash,
    ):
      result = convert_to_srt(input_path, output_path)

    self.assertTrue(result)
    run.assert_called_once_with(
      [
        'ffmpeg',
        '-v',
        'error',
        '-n',
        '-i',
        input_path,
        '-c:s',
        'srt',
        output_path,
      ],
      check=False,
      capture_output=True,
      encoding='utf-8',
      errors='replace',
      text=True,
    )
    self.assertTrue(os.path.isfile(output_path))
    with open(output_path, encoding='utf-8') as output_file:
      self.assertIn('foo', output_file.read())
    trash.assert_called_once_with(input_path)

  def test_keeps_source_when_conversion_fails(self):
    input_path = os.path.join(self.dir_path, 'foo.ass')
    output_path = os.path.join(self.dir_path, 'foo.srt')
    with open(input_path, 'w', encoding='utf-8') as input_file:
      input_file.write('subtitle fixture')

    def run_ffmpeg(command, **kwargs):
      with open(command[-1], 'w', encoding='utf-8') as output_file:
        output_file.write('partial output')
      return SimpleNamespace(returncode=1, stderr='conversion failed')

    with (
      patch('convert_to_srt.subprocess.run', side_effect=run_ffmpeg) as run,
      patch('convert_to_srt.send2trash') as trash,
    ):
      result = convert_to_srt(input_path, output_path)

    self.assertFalse(result)
    run.assert_called_once_with(
      [
        'ffmpeg',
        '-v',
        'error',
        '-n',
        '-i',
        input_path,
        '-c:s',
        'srt',
        output_path,
      ],
      check=False,
      capture_output=True,
      encoding='utf-8',
      errors='replace',
      text=True,
    )
    trash.assert_not_called()
    self.assertTrue(os.path.isfile(input_path))
    self.assertFalse(os.path.exists(output_path))

  def test_skips_when_output_already_exists(self):
    input_path = os.path.join(self.dir_path, 'foo.ssa')
    output_path = os.path.join(self.dir_path, 'foo.srt')
    for path in [input_path, output_path]:
      with open(path, 'w', encoding='utf-8'):
        pass

    with (
      patch('convert_to_srt.subprocess.run') as run,
      patch('convert_to_srt.send2trash') as trash,
    ):
      result = convert_to_srt(input_path, output_path)

    self.assertFalse(result)
    run.assert_not_called()
    trash.assert_not_called()

  def test_skips_srt_inputs(self):
    input_path = os.path.join(self.dir_path, 'foo.srt')
    with open(input_path, 'w', encoding='utf-8') as input_file:
      input_file.write('foo')

    process_file(input_path)

    with open(input_path, encoding='utf-8') as input_file:
      self.assertEqual(input_file.read(), 'foo')

  def test_skips_ass_when_positioning_is_not_confirmed(self):
    input_path = os.path.join(self.dir_path, 'foo.ass')
    with open(input_path, 'w', encoding='utf-8') as input_file:
      input_file.write(
        '[Events]\n'
        'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
        r'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,{\pos(100,200)}Hello'
      )

    with (
      patch('convert_to_srt.Prompt.bool', return_value=False) as prompt,
      patch('convert_to_srt.convert_to_srt') as convert,
    ):
      process_file(input_path)

    prompt.assert_called_once_with(
      f'Converting "{input_path}" to SRT will lose positioning or background data. Continue?',
      default=False,
    )
    convert.assert_not_called()

  def test_does_not_prompt_for_font_only_ass(self):
    input_path = os.path.join(self.dir_path, 'foo.ass')
    output_path = os.path.join(self.dir_path, 'foo.srt')
    with open(input_path, 'w', encoding='utf-8') as input_file:
      input_file.write(
        '[V4+ Styles]\n'
        'Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, BorderStyle, Alignment\n'
        'Style: Default,Arial,20,&H00FFFFFF,&HFF000000,1,2\n'
        '[Events]\n'
        'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
        'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,Hello\n'
      )

    with (
      patch('convert_to_srt.Prompt.bool') as prompt,
      patch('convert_to_srt.convert_to_srt') as convert,
    ):
      process_file(input_path)

    prompt.assert_not_called()
    convert.assert_called_once_with(input_path, output_path)

  def test_prompts_for_vtt_positioning(self):
    input_path = os.path.join(self.dir_path, 'foo.vtt')
    with open(input_path, 'w', encoding='utf-8') as input_file:
      input_file.write(
        'WEBVTT\n\n00:00:00.000 --> 00:00:01.000 position:10%\nHello\n'
      )

    with (
      patch('convert_to_srt.Prompt.bool', return_value=False) as prompt,
      patch('convert_to_srt.convert_to_srt') as convert,
    ):
      process_file(input_path)

    prompt.assert_called_once()
    convert.assert_not_called()

  def test_prompts_for_ass_box_background(self):
    input_path = os.path.join(self.dir_path, 'foo.ass')
    with open(input_path, 'w', encoding='utf-8') as input_file:
      input_file.write(
        '[V4+ Styles]\n'
        'Format: Name, Fontname, Fontsize, BackColour, BorderStyle, Alignment\n'
        'Style: Box,Arial,20,&H00000000,3,2\n'
        '[Events]\n'
        'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
        'Dialogue: 0,0:00:01.00,0:00:02.00,Box,,0,0,0,,Hello\n'
      )

    with (
      patch('convert_to_srt.Prompt.bool', return_value=False) as prompt,
      patch('convert_to_srt.convert_to_srt') as convert,
    ):
      process_file(input_path)

    prompt.assert_called_once()
    convert.assert_not_called()


if __name__ == '__main__':
  unittest.main()

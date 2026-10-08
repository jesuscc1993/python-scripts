import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from conver_to_srt import convert_to_srt, process_file

class TestConvertToSrt(unittest.TestCase):
  def test_moves_source_to_trash_after_successful_conversion(self):
    with tempfile.TemporaryDirectory() as dir_path:
      input_path = os.path.join(dir_path, 'foo.ass')
      output_path = os.path.join(dir_path, 'foo.srt')
      with open(input_path, 'w', encoding = 'utf-8'):
        pass

      def run_ffmpeg(command, **kwargs):
        with open(command[-1], 'w', encoding = 'utf-8') as output_file:
          output_file.write('foo')
        return SimpleNamespace(returncode = 0, stderr = '')

      with patch('conver_to_srt.subprocess.run', side_effect = run_ffmpeg) as run, patch('conver_to_srt.post_process_subs_file') as post_process, patch('conver_to_srt.send2trash') as trash:
        result = convert_to_srt(input_path, output_path)

      self.assertTrue(result)
      self.assertEqual(run.call_args.args[0][-1], output_path)
      post_process.assert_called_once_with(output_path, '.srt')
      trash.assert_called_once_with(input_path)
      self.assertTrue(os.path.isfile(output_path))

  def test_keeps_source_when_conversion_fails(self):
    with tempfile.TemporaryDirectory() as dir_path:
      input_path = os.path.join(dir_path, 'foo.vtt')
      output_path = os.path.join(dir_path, 'foo.srt')
      with open(input_path, 'w', encoding = 'utf-8'):
        pass

      with patch('conver_to_srt.subprocess.run', return_value = SimpleNamespace(returncode = 1, stderr = 'conversion failed')), patch('conver_to_srt.send2trash') as trash:
        result = convert_to_srt(input_path, output_path)

      self.assertFalse(result)
      trash.assert_not_called()
      self.assertTrue(os.path.isfile(input_path))
      self.assertFalse(os.path.exists(output_path))

  def test_skips_when_output_already_exists(self):
    with tempfile.TemporaryDirectory() as dir_path:
      input_path = os.path.join(dir_path, 'foo.ssa')
      output_path = os.path.join(dir_path, 'foo.srt')
      for path in [input_path, output_path]:
        with open(path, 'w', encoding = 'utf-8'):
          pass

      with patch('conver_to_srt.subprocess.run') as run, patch('conver_to_srt.send2trash') as trash:
        result = convert_to_srt(input_path, output_path)

      self.assertFalse(result)
      run.assert_not_called()
      trash.assert_not_called()

  def test_skips_srt_inputs(self):
    with patch('conver_to_srt.convert_to_srt') as convert:
      process_file('foo.srt')

    convert.assert_not_called()

if __name__ == '__main__':
  unittest.main()
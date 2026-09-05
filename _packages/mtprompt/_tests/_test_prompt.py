import io
import os
import sys
import tempfile
import unittest

from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mtprompt import Prompt, to_bool, to_int, to_path, to_dir, to_file

class ToBoolTests(unittest.TestCase):

  def test_yes_variants(self):
    self.assertTrue(to_bool('y'))
    self.assertTrue(to_bool('Y'))
    self.assertTrue(to_bool('yes'))
    self.assertTrue(to_bool('YES'))
    self.assertTrue(to_bool('  yes  '))

  def test_no_variants(self):
    self.assertFalse(to_bool('n'))
    self.assertFalse(to_bool('N'))
    self.assertFalse(to_bool('no'))
    self.assertFalse(to_bool('NO'))

  def test_invalid_raises(self):
    with self.assertRaises(ValueError):
      to_bool('foo')

class ToIntTests(unittest.TestCase):

  def test_valid(self):
    self.assertEqual(to_int('42'), 42)
    self.assertEqual(to_int('  15  '), 15)

  def test_invalid_raises(self):
    with self.assertRaises(ValueError):
      to_int('foo')

class ToPathTests(unittest.TestCase):

  def setUp(self):
    self.tmp_dir = tempfile.mkdtemp()
    self.tmp_file = os.path.join(self.tmp_dir, 'file.txt')
    with open(self.tmp_file, 'w') as f:
      f.write('data')

  def test_existing_path(self):
    self.assertEqual(to_path(self.tmp_dir), self.tmp_dir)
    self.assertEqual(to_path(f'"{self.tmp_dir}"'), self.tmp_dir)

  def test_missing_path_raises(self):
    with self.assertRaises(ValueError):
      to_path(os.path.join(self.tmp_dir, 'missing'))

  def test_dir(self):
    self.assertEqual(to_dir(self.tmp_dir), self.tmp_dir)
    with self.assertRaises(ValueError):
      to_dir(self.tmp_file)

  def test_file(self):
    self.assertEqual(to_file(self.tmp_file), self.tmp_file)
    with self.assertRaises(ValueError):
      to_file(self.tmp_dir)

class PromptIntTests(unittest.TestCase):

  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with patch('builtins.input', side_effect = lambda _ = '': next(input_iter)), redirect_stdout(io.StringIO()):
      return Prompt.int('p', **kwargs)

  def test_valid(self):
    self.assertEqual(self.call(['42']), 42)

  def test_retries_on_invalid(self):
    self.assertEqual(self.call(['foo', '7']), 7)

  def test_optional_empty(self):
    self.assertIsNone(self.call([''], optional = True))

  def test_default_on_empty(self):
    self.assertEqual(self.call([''], default = 9), 9)

class PromptBoolTests(unittest.TestCase):

  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with patch('builtins.input', side_effect = lambda _ = '': next(input_iter)), redirect_stdout(io.StringIO()):
      return Prompt.bool('p', **kwargs)

  def test_yes(self):
    self.assertTrue(self.call(['y']))

  def test_no(self):
    self.assertFalse(self.call(['n']))

  def test_invalid_falls_back_to_default(self):
    self.assertTrue(self.call(['foo'], default = True))
    self.assertFalse(self.call(['foo'], default = False))

  def test_retries_when_required(self):
    self.assertTrue(self.call(['', 'y']))

if __name__ == '__main__':
  unittest.main()

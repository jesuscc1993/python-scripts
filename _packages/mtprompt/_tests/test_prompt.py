import io
import os
import sys
import tempfile
import unittest

from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtprompt import (
  Prompt,
  to_bool,
  to_float,
  to_int,
  to_list,
  to_path,
  to_dir,
  to_file,
)


class ToBoolTests(unittest.TestCase):
  def test_yes_variants(self):
    self.assertTrue(to_bool('y'))
    self.assertTrue(to_bool('Y'))
    self.assertTrue(to_bool('yes'))
    self.assertTrue(to_bool('YES'))
    self.assertTrue(to_bool('true'))
    self.assertTrue(to_bool('TRUE'))
    self.assertTrue(to_bool('  yes  '))

  def test_no_variants(self):
    self.assertFalse(to_bool('n'))
    self.assertFalse(to_bool('N'))
    self.assertFalse(to_bool('no'))
    self.assertFalse(to_bool('NO'))
    self.assertFalse(to_bool('false'))
    self.assertFalse(to_bool('FALSE'))

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


class ToFloatTests(unittest.TestCase):
  def test_valid(self):
    self.assertEqual(to_float('4.2'), 4.2)
    self.assertEqual(to_float('  15  '), 15.0)

  def test_invalid_raises(self):
    with self.assertRaises(ValueError):
      to_float('foo')


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


class ToListTests(unittest.TestCase):
  def test_splits_unquoted_items(self):
    self.assertEqual(to_list('foo,bar'), ['foo', 'bar'])

  def test_parses_double_quoted_item(self):
    self.assertEqual(to_list('"foo",bar'), ['foo', 'bar'])

  def test_parses_single_quoted_item(self):
    self.assertEqual(to_list("'foo',bar"), ['foo', 'bar'])

  def test_preserves_commas_inside_quotes(self):
    self.assertEqual(to_list('foo,"bar,baz"'), ['foo', 'bar,baz'])

  def test_invalid_raises(self):
    with self.assertRaises(ValueError):
      to_list('"foo,bar')


class PromptStrTests(unittest.TestCase):
  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with (
      patch('builtins.input', side_effect=lambda _='': next(input_iter)),
      redirect_stdout(io.StringIO()),
    ):
      return Prompt.str('p', **kwargs)

  def test_valid(self):
    self.assertEqual(self.call(['foo']), 'foo')

  def test_retries_on_required_empty(self):
    self.assertEqual(self.call(['', 'foo']), 'foo')

  def test_optional_empty(self):
    self.assertIsNone(self.call([''], optional=True))

  def test_default_on_empty(self):
    self.assertEqual(self.call([''], default='foo'), 'foo')


class PromptListTests(unittest.TestCase):
  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with (
      patch('builtins.input', side_effect=lambda _='': next(input_iter)),
      redirect_stdout(io.StringIO()),
    ):
      return Prompt.list('p', **kwargs)

  def test_splits_unquoted_items(self):
    self.assertEqual(self.call(['foo,bar']), ['foo', 'bar'])

  def test_removes_quotes_from_items(self):
    self.assertEqual(self.call(['"foo",bar']), ['foo', 'bar'])

  def test_preserves_commas_inside_quotes(self):
    self.assertEqual(self.call(['foo,"bar,baz"']), ['foo', 'bar,baz'])

  def test_strips_item_whitespace(self):
    self.assertEqual(self.call([' foo, bar ']), ['foo', 'bar'])

  def test_retries_on_malformed_input(self):
    self.assertEqual(self.call(['"foo,bar', 'foo,bar']), ['foo', 'bar'])

  def test_optional_empty(self):
    self.assertIsNone(self.call([''], optional=True))

  def test_default_on_empty(self):
    self.assertEqual(self.call([''], default=['foo']), ['foo'])


class PromptOptionTests(unittest.TestCase):
  def call(self, inputs, options=None, **kwargs):
    if options is None:
      options = ['foo', 'bar', 'baz']
    input_iter = iter(inputs)
    with (
      patch('builtins.input', side_effect=lambda _='': next(input_iter)),
      redirect_stdout(io.StringIO()),
    ):
      return Prompt.option(options, 'p', **kwargs)

  def test_valid(self):
    self.assertEqual(self.call(['2']), 'bar')

  def test_retries_on_non_digit(self):
    self.assertEqual(self.call(['foo', '1']), 'foo')

  def test_retries_on_out_of_range(self):
    self.assertEqual(self.call(['9', '3']), 'baz')

  def test_optional_empty(self):
    self.assertIsNone(self.call([''], optional=True))

  def test_default_on_empty(self):
    self.assertEqual(self.call([''], default='bar'), 'bar')

  def test_accepts_non_string_items(self):
    self.assertEqual(self.call(['2'], options=[1, 2, 3]), 2)

  def test_raises_on_non_list(self):
    with self.assertRaises(TypeError):
      self.call(['1'], options='foo,bar')


class PromptIntTests(unittest.TestCase):
  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with (
      patch('builtins.input', side_effect=lambda _='': next(input_iter)),
      redirect_stdout(io.StringIO()),
    ):
      return Prompt.int('p', **kwargs)

  def test_valid(self):
    self.assertEqual(self.call(['42']), 42)

  def test_retries_on_invalid(self):
    self.assertEqual(self.call(['foo', '7']), 7)

  def test_optional_empty(self):
    self.assertIsNone(self.call([''], optional=True))

  def test_default_on_empty(self):
    self.assertEqual(self.call([''], default=9), 9)


class PromptFloatTests(unittest.TestCase):
  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with (
      patch('builtins.input', side_effect=lambda _='': next(input_iter)),
      redirect_stdout(io.StringIO()),
    ):
      return Prompt.float('p', **kwargs)

  def test_valid(self):
    self.assertEqual(self.call(['4.2']), 4.2)

  def test_retries_on_invalid(self):
    self.assertEqual(self.call(['foo', '0.7']), 0.7)

  def test_optional_empty(self):
    self.assertIsNone(self.call([''], optional=True))

  def test_default_on_empty(self):
    self.assertEqual(self.call([''], default=0.9), 0.9)


class PromptBoolTests(unittest.TestCase):
  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with (
      patch('builtins.input', side_effect=lambda _='': next(input_iter)),
      redirect_stdout(io.StringIO()),
    ):
      return Prompt.bool('p', **kwargs)

  def test_yes(self):
    self.assertTrue(self.call(['y']))

  def test_no(self):
    self.assertFalse(self.call(['n']))

  def test_invalid_falls_back_to_default(self):
    self.assertTrue(self.call(['foo'], default=True))
    self.assertFalse(self.call(['foo'], default=False))

  def test_retries_when_required(self):
    self.assertTrue(self.call(['', 'y']))


class PromptPathTests(unittest.TestCase):
  def setUp(self):
    self.tmp_dir = tempfile.mkdtemp()
    self.tmp_file = os.path.join(self.tmp_dir, 'file.txt')
    with open(self.tmp_file, 'w') as f:
      f.write('data')

  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with (
      patch('builtins.input', side_effect=lambda _='': next(input_iter)),
      redirect_stdout(io.StringIO()),
    ):
      return Prompt.path('p', **kwargs)

  def test_valid(self):
    self.assertEqual(self.call([self.tmp_file]), self.tmp_file)

  def test_retries_on_missing_path(self):
    missing = os.path.join(self.tmp_dir, 'missing')
    self.assertEqual(self.call([missing, self.tmp_dir]), self.tmp_dir)

  def test_optional_empty(self):
    self.assertIsNone(self.call([''], optional=True))

  def test_default_on_empty(self):
    self.assertEqual(self.call([''], default=self.tmp_dir), self.tmp_dir)


class PromptDirTests(unittest.TestCase):
  def setUp(self):
    self.tmp_dir = tempfile.mkdtemp()
    self.tmp_file = os.path.join(self.tmp_dir, 'file.txt')
    with open(self.tmp_file, 'w') as f:
      f.write('data')

  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with (
      patch('builtins.input', side_effect=lambda _='': next(input_iter)),
      redirect_stdout(io.StringIO()),
    ):
      return Prompt.dir('p', **kwargs)

  def test_valid(self):
    self.assertEqual(self.call([self.tmp_dir]), self.tmp_dir)

  def test_retries_on_file_path(self):
    self.assertEqual(self.call([self.tmp_file, self.tmp_dir]), self.tmp_dir)

  def test_optional_empty(self):
    self.assertIsNone(self.call([''], optional=True))

  def test_default_on_empty(self):
    self.assertEqual(self.call([''], default=self.tmp_dir), self.tmp_dir)


class PromptFileTests(unittest.TestCase):
  def setUp(self):
    self.tmp_dir = tempfile.mkdtemp()
    self.tmp_file = os.path.join(self.tmp_dir, 'file.txt')
    with open(self.tmp_file, 'w') as f:
      f.write('data')

  def call(self, inputs, **kwargs):
    input_iter = iter(inputs)
    with (
      patch('builtins.input', side_effect=lambda _='': next(input_iter)),
      redirect_stdout(io.StringIO()),
    ):
      return Prompt.file('p', **kwargs)

  def test_valid(self):
    self.assertEqual(self.call([self.tmp_file]), self.tmp_file)

  def test_retries_on_dir_path(self):
    self.assertEqual(self.call([self.tmp_dir, self.tmp_file]), self.tmp_file)

  def test_optional_empty(self):
    self.assertIsNone(self.call([''], optional=True))

  def test_default_on_empty(self):
    self.assertEqual(self.call([''], default=self.tmp_file), self.tmp_file)


if __name__ == '__main__':
  unittest.main()

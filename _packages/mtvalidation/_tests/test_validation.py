import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtprompt import (
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


if __name__ == '__main__':
  unittest.main()

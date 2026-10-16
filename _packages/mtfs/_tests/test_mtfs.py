import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mtattr import Attr
from mtfs import (
  read_file,
  read_json_file,
  read_metadata,
  read_text_file,
  write_file,
  write_json_file,
  write_metadata,
  write_text_file,
)

TEST_DIR = os.path.join(tempfile.gettempdir(), 'mtfs-tests')


class MtfsTests(unittest.TestCase):
  def setUp(self):
    shutil.rmtree(TEST_DIR, ignore_errors=True)
    os.makedirs(TEST_DIR)

  def tearDown(self):
    shutil.rmtree(TEST_DIR, ignore_errors=True)

  def test_missing_file_returns_none(self):
    self.assertIsNone(read_file(os.path.join(TEST_DIR, 'missing.bin')))
    self.assertIsNone(read_text_file(os.path.join(TEST_DIR, 'missing.txt')))
    self.assertIsNone(read_json_file(os.path.join(TEST_DIR, 'missing.json')))

  def test_binary_file_round_trip(self):
    path = os.path.join(TEST_DIR, 'nested', 'data.bin')
    content = bytes([0, 255, 1])

    write_file(path, content)

    self.assertEqual(read_file(path), content)

  def test_text_file_round_trip(self):
    path = os.path.join(TEST_DIR, 'nested', 'data.txt')

    write_text_file(path, 'foo')

    self.assertEqual(read_text_file(path), 'foo')

  def test_text_file_cp1252_fallback(self):
    path = os.path.join(TEST_DIR, 'data.txt')
    content = 'café'

    with open(path, 'wb') as file:
      file.write(content.encode('cp1252'))

    self.assertEqual(read_text_file(path), content)

    with open(path, 'rb') as file:
      self.assertEqual(file.read(), content.encode('utf-8'))

  def test_text_file_custom_encoding(self):
    path = os.path.join(TEST_DIR, 'data.txt')
    content = 'café'

    write_text_file(path, content, encoding='latin-1')

    self.assertEqual(read_text_file(path, encoding='latin-1'), content)

  def test_text_file_cp1252_fallback_custom_encoding(self):
    path = os.path.join(TEST_DIR, 'data.txt')
    content = 'café'

    with open(path, 'wb') as file:
      file.write(content.encode('cp1252'))

    self.assertEqual(read_text_file(path, encoding='latin-1'), content)

    with open(path, 'rb') as file:
      self.assertEqual(file.read(), content.encode('latin-1'))

  def test_json_file_round_trip(self):
    path = os.path.join(TEST_DIR, 'nested', 'data.json')
    content = {'foo': ['bar', 1]}

    write_json_file(path, content)

    self.assertEqual(read_json_file(path), content)

  def test_read_metadata_missing_returns_none(self):
    self.assertIsNone(read_metadata(os.path.join(TEST_DIR, 'foo')))

  def test_metadata_round_trip(self):
    dir_path = os.path.join(TEST_DIR, 'foo')
    os.makedirs(dir_path)
    content = {'size': 123, 'bar': 'baz'}

    write_metadata(dir_path, content)

    self.assertEqual(read_metadata(dir_path), content)

  def test_write_metadata_hides_file(self):
    dir_path = os.path.join(TEST_DIR, 'foo')
    os.makedirs(dir_path)

    write_metadata(dir_path, {'size': 123})

    self.assertTrue(Attr.is_hidden(os.path.join(dir_path, 'metadata.json')))

  def test_read_metadata_invalid_json_raises_type_error(self):
    dir_path = os.path.join(TEST_DIR, 'foo')
    os.makedirs(dir_path)
    write_json_file(os.path.join(dir_path, 'metadata.json'), ['bar', 'baz'])

    with self.assertRaises(TypeError):
      read_metadata(dir_path)


if __name__ == '__main__':
  unittest.main()

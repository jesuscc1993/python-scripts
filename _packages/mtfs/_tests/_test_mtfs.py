import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mtfs import read_file, read_json_file, read_text_file, write_file, write_json_file, write_text_file

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

  def test_json_file_round_trip(self):
    path = os.path.join(TEST_DIR, 'nested', 'data.json')
    content = {'foo': ['bar', 1]}

    write_json_file(path, content)

    self.assertEqual(read_json_file(path), content)

if __name__ == '__main__':
  unittest.main()

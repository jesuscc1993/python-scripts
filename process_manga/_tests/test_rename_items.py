import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from rename_items import get_processed_name

def name(filename, is_dir=False):
  with patch('os.path.isdir', return_value=is_dir):
    return get_processed_name(f'/fake/{filename}')

class TestChapterPrettify(unittest.TestCase):
  def test_chapter_word(self):
    self.assertEqual(name('Chapter 1.cbz'), 'Ch.001.cbz')

  def test_chapter_short(self):
    self.assertEqual(name('Ch 42.cbz'), 'Ch.042.cbz')

  def test_chapter_dot(self):
    self.assertEqual(name('Ch.5.cbz'), 'Ch.005.cbz')

  def test_chapter_decimal(self):
    self.assertEqual(name('Ch 1.4.cbz'), 'Ch.001.4.cbz')

class TestVolumePrettify(unittest.TestCase):
  def test_vol(self):
    self.assertEqual(name('Vol 1.cbz'), 'Vol.01.cbz')

  def test_volume_word(self):
    self.assertEqual(name('Volume 12.cbz'), 'Vol.12.cbz')

  def test_vol_dot(self):
    self.assertEqual(name('Vol.3.cbz'), 'Vol.03.cbz')

  def test_cbz_volume_becomes_cbz(self):
    self.assertEqual(name('Vol.01.zip'), 'Vol.01.cbz')

class TestTagRemoval(unittest.TestCase):
  def test_removes_official(self):
    self.assertEqual(name('My Manga (Official) Ch.001.cbz'), 'My Manga Ch.001.cbz')

  def test_removes_index(self):
    self.assertEqual(name('My Manga [5] Ch.001.cbz'), 'My Manga Ch.001.cbz')

class TestDuplicateChapter(unittest.TestCase):
  def test_duplicate_ch_fix(self):
    self.assertEqual(name('Ch.001 - Ch.001.cbz'), 'Ch.001.cbz')

  def test_no_false_positive(self):
    self.assertEqual(name('Ch.001 - Ch.002.cbz'), 'Ch.001 - Ch.002.cbz')

class TestSeasonShorten(unittest.TestCase):
  def test_season(self):
    self.assertEqual(name('Season 1.cbz'), 'S1.cbz')

  def test_epilogue(self):
    self.assertEqual(name('Epilogue 1.cbz'), 'EP1.cbz')

  def test_side_story(self):
    self.assertEqual(name('Side Story 1.cbz'), 'SS1.cbz')

  def test_special(self):
    self.assertEqual(name('Special 1.cbz'), 'SP1.cbz')

class TestImageSkip(unittest.TestCase):
  def test_image_skipped(self):
    self.assertEqual(name('Volume 1 Chapter 1 Page 1.jpg'), 'Volume 1 Chapter 1 Page 1.jpg')

class TestWhitespace(unittest.TestCase):
  def test_extra_spaces_removed(self):
    self.assertEqual(name('foo  bar.cbz'), 'foo bar.cbz')

class TestDirectory(unittest.TestCase):
  def test_dir_no_ext(self):
    result = name('Chapter 1', is_dir=True)
    self.assertEqual(result, 'Ch.001')

if __name__ == '__main__':
  unittest.main()

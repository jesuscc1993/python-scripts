import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from _common import calc_fit_size, center_offset, is_image_file, round_to_even

class RoundToEvenTests(unittest.TestCase):

  def test_rounds_down_to_nearest_even(self):
    self.assertEqual(round_to_even(204.8), 204)

  def test_rounds_up_to_nearest_even(self):
    self.assertEqual(round_to_even(409.6), 410)

  def test_ties_round_to_even(self):
    self.assertEqual(round_to_even(203), 204)

class CalcFitSizeTests(unittest.TestCase):

  def test_scales_to_fit_within_target_box(self):
    self.assertEqual(calc_fit_size(100, 50, 200, 200), (200, 100))

  def test_returns_target_size_when_aspect_matches(self):
    self.assertEqual(calc_fit_size(100, 100, 50, 50), (50, 50))

class IsImageFileTests(unittest.TestCase):

  def test_accepts_supported_extensions(self):
    self.assertTrue(is_image_file('foo.png'))
    self.assertTrue(is_image_file('foo.jpg'))
    self.assertTrue(is_image_file('foo.jpeg'))
    self.assertTrue(is_image_file('foo.webp'))
    self.assertTrue(is_image_file('foo.svg'))

  def test_is_case_insensitive(self):
    self.assertTrue(is_image_file('foo.PNG'))

  def test_rejects_unsupported_extension(self):
    self.assertFalse(is_image_file('foo.txt'))

  def test_rejects_missing_extension(self):
    self.assertFalse(is_image_file('foo'))

class CenterOffsetTests(unittest.TestCase):

  def test_centers_smaller_image_in_canvas(self):
    self.assertEqual(center_offset((200, 200), (100, 50)), (50, 75))

  def test_returns_zero_offset_when_same_size(self):
    self.assertEqual(center_offset((100, 100), (100, 100)), (0, 0))

if __name__ == '__main__':
  unittest.main()

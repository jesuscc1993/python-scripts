import os
import sys
import unittest

import numpy
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from crop_webtoon import crop_blanks, is_blank_strip


class TestCropWebtoon(unittest.TestCase):
  def test_returns_same_rgb_image_when_there_are_no_blank_strips(self):
    image = Image.new('RGB', (3, 10), (100, 120, 140))

    result = crop_blanks(image)

    self.assertIs(result, image)

  def test_converts_non_rgb_image_when_there_are_no_blank_strips(self):
    image = Image.new('L', (3, 10), 100)

    result = crop_blanks(image)

    self.assertEqual(result.mode, 'RGB')
    numpy.testing.assert_array_equal(
      numpy.array(result), numpy.array(image.convert('RGB'))
    )

  def test_clears_metadata_from_rgb_image_without_copying(self):
    image = Image.new('RGB', (3, 10), (100, 120, 140))
    image.info['description'] = 'foo'

    result = crop_blanks(image)

    self.assertIs(result, image)
    self.assertEqual(result.info, {})
    numpy.testing.assert_array_equal(numpy.array(result), numpy.array(image))

  def test_blank_detection_keeps_threshold_boundaries(self):
    cases = (
      (numpy.array([[248, 255]], dtype=numpy.uint8), True),
      (numpy.array([[247, 255]], dtype=numpy.uint8), False),
      (numpy.array([[0, 8]], dtype=numpy.uint8), True),
      (numpy.array([[0, 9]], dtype=numpy.uint8), False),
    )

    for strip, expected in cases:
      with self.subTest(strip=strip.tolist()):
        self.assertEqual(is_blank_strip(strip), expected)

  def test_groups_content_bands_and_preserves_partial_final_band(self):
    image = Image.new('RGB', (2, 173), (100, 120, 140))
    image.paste(Image.new('RGB', (2, 96), (255, 255, 255)), (0, 48))

    result = crop_blanks(image)

    expected = Image.new('RGB', (2, 125))
    expected.paste(image.crop((0, 0, 2, 48)), (0, 0))
    expected.paste(Image.new('RGB', (2, 48), (255, 255, 255)), (0, 48))
    expected.paste(image.crop((0, 144, 2, 173)), (0, 96))
    self.assertEqual(result.size, expected.size)
    numpy.testing.assert_array_equal(numpy.array(result), numpy.array(expected))


if __name__ == '__main__':
  unittest.main()

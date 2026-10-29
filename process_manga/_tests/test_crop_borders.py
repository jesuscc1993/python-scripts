import os
import sys
import unittest

import numpy
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from crop_borders import crop_blanks


class TestCropBlanks(unittest.TestCase):
  def test_returns_original_image_when_all_pixels_are_white(self):
    image = Image.new('L', (6, 5), 255)

    result = crop_blanks(image, True, True)

    self.assertIs(result, image)

  def test_crops_grayscale_content_to_exact_bounds(self):
    pixels = numpy.full((5, 6), 255, dtype=numpy.uint8)
    pixels[1:4, 2:5] = 100

    result = crop_blanks(Image.fromarray(pixels), True, True)

    self.assertEqual(result.size, (3, 3))
    numpy.testing.assert_array_equal(numpy.array(result), pixels[1:4, 2:5])

  def test_crops_only_vertical_borders_when_requested(self):
    pixels = numpy.full((5, 6), 255, dtype=numpy.uint8)
    pixels[1:4, 2:5] = 100

    result = crop_blanks(
      Image.fromarray(pixels),
      should_crop_vertically=True,
      should_crop_horizontally=False,
    )

    self.assertEqual(result.size, (6, 3))
    numpy.testing.assert_array_equal(numpy.array(result), pixels[1:4, :])

  def test_crops_only_horizontal_borders_when_requested(self):
    pixels = numpy.full((5, 6), 255, dtype=numpy.uint8)
    pixels[1:4, 2:5] = 100

    result = crop_blanks(
      Image.fromarray(pixels),
      should_crop_vertically=False,
      should_crop_horizontally=True,
    )

    self.assertEqual(result.size, (3, 5))
    numpy.testing.assert_array_equal(numpy.array(result), pixels[:, 2:5])

  def test_crops_rgb_content_using_any_channel_below_threshold(self):
    pixels = numpy.full((5, 6, 3), 255, dtype=numpy.uint8)
    pixels[1, 2, 0] = 247
    pixels[3, 4, 1] = 247

    result = crop_blanks(Image.fromarray(pixels), True, True)

    self.assertEqual(result.size, (3, 3))
    numpy.testing.assert_array_equal(numpy.array(result), pixels[1:4, 2:5])


if __name__ == '__main__':
  unittest.main()

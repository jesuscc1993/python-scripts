import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from delete_image_matches import process_chapter


class FakeHash:
  def __init__(self, value):
    self.value = value

  def __sub__(self, other):
    return abs(self.value - other.value)


class TestProcessChapter(unittest.TestCase):
  def test_hashes_each_target_image_only_once(self):
    target_images = ['page1.webp', 'page2.webp', 'page3.webp']
    trashed_images = []
    image_hashes = {
      'page1.webp': FakeHash(100),
      'page2.webp': FakeHash(20),
      'page3.webp': FakeHash(40),
    }
    ref_hashes = [FakeHash(20), FakeHash(40)]

    def list_target_images(chapter_folder, img_spot):
      return [path for path in target_images if path not in trashed_images]

    def open_image(path):
      image_file = MagicMock()
      image_file.__enter__.return_value = path
      return image_file

    with (
      patch(
        'delete_image_matches.get_images_by_spot',
        side_effect=list_target_images,
      ),
      patch('delete_image_matches.Image.open', side_effect=open_image),
      patch(
        'delete_image_matches.imagehash.phash',
        side_effect=lambda image: image_hashes[image],
      ) as phash,
      patch(
        'delete_image_matches.send2trash',
        side_effect=trashed_images.append,
      ),
      patch('delete_image_matches.tqdm.write'),
    ):
      deleted = process_chapter('chapter', ref_hashes, 0)

    self.assertEqual(deleted, 2)
    self.assertEqual(trashed_images, ['page2.webp', 'page3.webp'])
    self.assertEqual(
      [call.args[0] for call in phash.call_args_list], target_images
    )


if __name__ == '__main__':
  unittest.main()

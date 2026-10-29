import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from delete_stale_subs import find_stale_subtitle_files


class TestFindStaleSubtitleFiles(unittest.TestCase):
  def test_finds_orphans_and_matches_subtitle_folders_to_parent_videos(self):
    root = os.path.join('foo', 'bar')
    subtitles_dir = os.path.join(root, 'subtitles')
    subs_dir = os.path.join(root, 'subs')
    walk_results = [
      (root, ['subtitles', 'subs'], ['movie.mkv', 'movie.srt', 'orphan.vtt']),
      (subtitles_dir, [], ['movie.ass', 'orphan.srt']),
      (subs_dir, [], ['movie.vtt', 'other-orphan.srt']),
    ]

    with patch('delete_stale_subs.os.walk', return_value=walk_results):
      stale_files = find_stale_subtitle_files(root)

    self.assertEqual(
      stale_files,
      [
        os.path.join(root, 'orphan.vtt'),
        os.path.join(subtitles_dir, 'orphan.srt'),
        os.path.join(subs_dir, 'other-orphan.srt'),
      ],
    )

  def test_matches_extensions_and_stems_without_case_sensitivity(self):
    root = os.path.join('foo', 'bar')
    walk_results = [(root, [], ['Movie.MP4', 'movie.SRT', 'notes.txt'])]

    with patch('delete_stale_subs.os.walk', return_value=walk_results):
      stale_files = find_stale_subtitle_files(root)

    self.assertEqual(stale_files, [])

  def test_keeps_subtitles_with_video_name_prefix_and_separator(self):
    root = os.path.join('foo', 'bar')
    walk_results = [
      (
        root,
        [],
        [
          'foo.mkv',
          'foo - Captions.ass',
          'foo_2.ass',
          'foobar.ass',
        ],
      )
    ]

    with patch('delete_stale_subs.os.walk', return_value=walk_results):
      stale_files = find_stale_subtitle_files(root)

    self.assertEqual(stale_files, [os.path.join(root, 'foobar.ass')])


if __name__ == '__main__':
  unittest.main()

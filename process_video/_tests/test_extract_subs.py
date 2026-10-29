import shutil
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from extract_subs import find_subtitle_streams, process_directory, process_file


class TestExtractSubs(unittest.TestCase):
  def test_finds_all_matching_streams_when_metadata_contains_invalid_bytes(
    self,
  ):
    output = (
      b'{"streams":['
      b'{"codec_type":"subtitle","codec_name":"subrip",'
      b'"index":2,"tags":{"language":"eng","title":"foo \xff"}},'
      b'{"codec_type":"subtitle","codec_name":"ass",'
      b'"index":3,"tags":{"language":"eng-US"}},'
      b'{"codec_type":"subtitle","codec_name":"subrip",'
      b'"index":4,"tags":{"language":"spa"}},'
      b'{"codec_type":"subtitle","codec_name":"unknown",'
      b'"index":5,"tags":{"language":"eng"}}]}'
    )

    def run_ffprobe(command, **kwargs):
      stdout = output.decode(kwargs['encoding'], errors=kwargs['errors'])
      return SimpleNamespace(stdout=stdout)

    with patch('extract_subs.subprocess.run', side_effect=run_ffprobe) as run:
      result = find_subtitle_streams('foo.mkv', 'eng')

    self.assertEqual(
      result,
      [(2, 'subrip', 'foo \ufffd'), (3, 'ass', None)],
    )
    self.assertEqual(run.call_args.kwargs['encoding'], 'utf-8')
    self.assertEqual(run.call_args.kwargs['errors'], 'replace')

  def test_extracts_all_tracks_to_distinct_file_names(self):
    with (
      patch(
        'extract_subs.find_subtitle_streams',
        return_value=[
          (2, 'subrip', 'English: Signs'),
          (3, 'subrip', 'English: Dialogue'),
        ],
      ),
      patch('extract_subs.SETTINGS', {'extract_to_folder': False}),
      patch('extract_subs.os.path.exists', return_value=False),
      patch('extract_subs.extract_subtitles') as extract,
    ):
      process_file('foo.mkv')

    self.assertEqual(
      [call.args for call in extract.call_args_list],
      [
        ('foo.mkv', 'foo - English Signs.srt', 'foo.mkv', 2, '.srt'),
        ('foo.mkv', 'foo - English Dialogue.srt', 'foo.mkv', 3, '.srt'),
      ],
    )

  def test_single_track_uses_video_name_without_track_title(self):
    with (
      patch(
        'extract_subs.find_subtitle_streams',
        return_value=[(2, 'subrip', 'English: Signs')],
      ),
      patch('extract_subs.SETTINGS', {'extract_to_folder': False}),
      patch('extract_subs.os.path.exists', return_value=False),
      patch('extract_subs.extract_subtitles') as extract,
    ):
      process_file('foo.mkv')

    extract.assert_called_once_with('foo.mkv', 'foo.srt', 'foo.mkv', 2, '.srt')

  def test_process_directory_skips_tmp_directories(self):
    dir_path = os.path.join(
      tempfile.gettempdir(),
      'python-scripts-tests',
      'process_video',
      'extract_subs',
      'process_directory_skips_tmp',
    )
    shutil.rmtree(dir_path, ignore_errors=True)
    tmp_dir = os.path.join(dir_path, '.tmp')
    os.makedirs(tmp_dir)
    video_path = os.path.join(dir_path, 'foo.mkv')
    with open(video_path, 'wb') as video_file:
      video_file.write(b'video fixture')
    temp_video_path = os.path.join(tmp_dir, 'bar.mkv')
    with open(temp_video_path, 'wb') as video_file:
      video_file.write(b'temporary video fixture')

    try:
      with patch('extract_subs.process_file') as process:
        process_directory(dir_path)

      process.assert_called_once_with(video_path)
    finally:
      shutil.rmtree(dir_path, ignore_errors=True)


if __name__ == '__main__':
  unittest.main()

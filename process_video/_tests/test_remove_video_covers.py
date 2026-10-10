import json
import os
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import remove_video_covers


class TestRemoveVideoCovers(unittest.TestCase):
  def setUp(self):
    self.dir_path = os.path.join(
      tempfile.gettempdir(),
      'python-scripts-tests',
      'process_video',
      'remove_video_covers',
      self._testMethodName,
    )
    shutil.rmtree(self.dir_path, ignore_errors=True)
    self.tmp_dir = os.path.join(self.dir_path, '.tmp')
    os.makedirs(self.tmp_dir)
    self.video_path = os.path.join(self.dir_path, 'foo.mkv')
    with open(self.video_path, 'wb') as video_file:
      video_file.write(b'video with cover')

  def tearDown(self):
    shutil.rmtree(self.dir_path, ignore_errors=True)

  def test_remuxes_without_cover_and_preserves_other_streams(self):
    streams = [
      {'index': 0, 'codec_type': 'video', 'disposition': {'attached_pic': 0}},
      {'index': 1, 'codec_type': 'audio'},
      {
        'index': 2,
        'codec_type': 'video',
        'disposition': {'attached_pic': 1},
        'tags': {'filename': 'cover.jpg', 'mimetype': 'image/jpeg'},
      },
      {
        'index': 3,
        'codec_type': 'attachment',
        'tags': {'filename': 'font.ttf'},
      },
    ]

    def run_command(command, **kwargs):
      if command[0] == 'ffprobe':
        return SimpleNamespace(
          returncode=0, stdout=json.dumps({'streams': streams}), stderr=''
        )
      with open(command[-1], 'wb') as output_file:
        output_file.write(b'video without cover')
      return SimpleNamespace(returncode=0, stderr=b'')

    with patch.object(
      remove_video_covers.subprocess, 'run', side_effect=run_command
    ) as run:
      result = remove_video_covers.remove_ffmpeg_covers(
        self.video_path, self.tmp_dir
      )

    self.assertTrue(result)
    with open(self.video_path, 'rb') as video_file:
      self.assertEqual(video_file.read(), b'video without cover')
    self.assertEqual(
      [call.args[0] for call in run.call_args_list],
      [
        [
          'ffprobe',
          '-v',
          'quiet',
          '-analyzeduration',
          '0',
          '-probesize',
          '5000000',
          '-print_format',
          'json',
          '-show_streams',
          self.video_path,
        ],
        [
          'ffmpeg',
          '-y',
          '-loglevel',
          'error',
          '-i',
          self.video_path,
          '-map',
          '0',
          '-map',
          '-0:2',
          '-c',
          'copy',
          os.path.join(self.tmp_dir, 'foo.mkv'),
        ],
      ],
    )

  def test_does_not_remux_when_no_cover_stream_exists(self):
    streams = [
      {'index': 0, 'codec_type': 'video', 'disposition': {'attached_pic': 0}}
    ]
    with patch.object(
      remove_video_covers.subprocess,
      'run',
      return_value=SimpleNamespace(
        returncode=0, stdout=json.dumps({'streams': streams}), stderr=''
      ),
    ) as run:
      result = remove_video_covers.remove_ffmpeg_covers(
        self.video_path, self.tmp_dir
      )

    self.assertFalse(result)
    run.assert_called_once()
    with open(self.video_path, 'rb') as video_file:
      self.assertEqual(video_file.read(), b'video with cover')

  def test_removes_mp4_cover_tag(self):
    class FakeMP4(dict):
      def __init__(self):
        super().__init__({'covr': ['cover data']})
        self.tags = self
        self.saved = False

      def save(self):
        self.saved = True

    media = FakeMP4()
    with patch.object(remove_video_covers, 'MP4', return_value=media):
      result = remove_video_covers.remove_mp4_cover(self.video_path)

    self.assertTrue(result)
    self.assertNotIn('covr', media)
    self.assertTrue(media.saved)


if __name__ == '__main__':
  unittest.main()

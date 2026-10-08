import json
import os
import shutil
import sys
import subprocess
import tempfile
import unittest
from types import SimpleNamespace

from PIL import Image
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import generate_video_covers

class TestGenerateVideoCovers(unittest.TestCase):
  def setUp(self):
    self.dir_path = os.path.join(
      tempfile.gettempdir(),
      'python-scripts-tests',
      'process_video',
      'generate_video_covers',
      self._testMethodName
    )
    shutil.rmtree(self.dir_path, ignore_errors=True)
    os.makedirs(self.dir_path)
    self.video_path = os.path.join(self.dir_path, 'foo.mkv')
    with open(self.video_path, 'wb') as video_file:
      video_file.write(b'video fixture')

  def tearDown(self):
    shutil.rmtree(self.dir_path, ignore_errors=True)

  def assert_video_was_replaced(self, video_path):
    with open(video_path, 'rb') as video_file:
      self.assertEqual(video_file.read(), b'covered video')

  def run_media_command(self, command, **kwargs):
    if command[0] == 'attrib':
      return SimpleNamespace(returncode=0, stdout='', stderr=b'')

    if command[0] == 'ffprobe':
      return SimpleNamespace(
        returncode=0,
        stdout=json.dumps({
          'format': {
            'duration': '4.0',
            'size': str(os.path.getsize(command[-1]))
          }
        }),
        stderr=''
      )

    if command[0] == 'ffmpeg' and '-vframes' in command:
      Image.new('RGB', (320, 180), color='red').save(command[-1], format='JPEG')
      return SimpleNamespace(returncode=0, stderr=b'')

    if command[0] == 'ffmpeg' and '-attach' in command:
      with open(command[-1], 'wb') as output_file:
        output_file.write(b'covered video')
      return SimpleNamespace(returncode=0, stderr=b'')

    self.fail(f'Unexpected subprocess command: {command}')

  def assert_ffmpeg_commands(self, run, video_path):
    tmp_dir = os.path.join(os.path.dirname(video_path), '.tmp')
    frame_path = os.path.join(tmp_dir, 'foo.jpg')
    output_path = os.path.join(tmp_dir, 'foo.mkv')
    commands = [
      call.args[0]
      for call in run.call_args_list
      if call.args[0][0] in ('ffmpeg', 'ffprobe')
    ]

    self.assertEqual(commands, [
      [
        'ffprobe', '-v', 'quiet', '-analyzeduration', '0',
        '-probesize', '5000000', '-print_format', 'json',
        '-show_format', video_path
      ],
      [
        'ffmpeg', '-y', '-loglevel', 'error', '-analyzeduration', '0',
        '-probesize', '5000000', '-ss', '1.0', '-i', video_path,
        '-vframes', '1', '-q:v', '2', frame_path
      ],
      [
        'ffmpeg', '-y', '-loglevel', 'error', '-i', video_path,
        '-attach', frame_path,
        '-metadata:s:t:0', 'mimetype=image/jpeg',
        '-metadata:s:t:0', 'filename=cover.jpg',
        '-c', 'copy', output_path
      ]
    ])

  def test_main_generates_cover_for_single_file(self):
    with patch.object(generate_video_covers.sys, 'argv', ['generate_video_covers.py', self.video_path]), \
        patch.object(generate_video_covers.subprocess, 'run', side_effect=self.run_media_command) as run, \
        patch.object(generate_video_covers.logger, 'log'), \
        patch.object(generate_video_covers.logger, 'hr'):
      generate_video_covers.main()

    self.assertTrue(os.path.isfile(self.video_path))
    self.assertFalse(os.path.exists(os.path.join(self.dir_path, '.tmp')))
    self.assert_video_was_replaced(self.video_path)
    self.assert_ffmpeg_commands(run, self.video_path)

  def test_main_generates_covers_for_folder(self):
    dir_path = os.path.join(self.dir_path, 'videos')
    os.makedirs(dir_path)
    video_path = os.path.join(dir_path, 'foo.mkv')
    os.replace(self.video_path, video_path)

    with patch.object(generate_video_covers.sys, 'argv', ['generate_video_covers.py', dir_path]), \
        patch.object(generate_video_covers.subprocess, 'run', side_effect=self.run_media_command) as run, \
      patch.object(generate_video_covers.logger, 'log'), \
      patch.object(generate_video_covers.logger, 'hr'):
      generate_video_covers.main()

    self.assertTrue(os.path.isfile(video_path))
    self.assertFalse(os.path.exists(os.path.join(dir_path, '.tmp')))
    self.assert_video_was_replaced(video_path)
    self.assert_ffmpeg_commands(run, video_path)

  def test_process_directory_skips_temp_directory(self):
    tmp_dir = os.path.join(self.dir_path, '.tmp')
    os.makedirs(tmp_dir)
    temp_video_path = os.path.join(tmp_dir, 'bar.mkv')
    with open(temp_video_path, 'wb') as video_file:
      video_file.write(b'temporary video')

    with patch.object(generate_video_covers, 'process_file') as process_file:
      generate_video_covers.process_directory(self.dir_path, tmp_dir)

    process_file.assert_called_once_with(self.video_path, tmp_dir)

  def test_embeds_cover_in_mp4_tag(self):
    tags = MagicMock()
    cover_data = b'cover image'

    with patch.object(generate_video_covers, 'read_file', return_value=cover_data), \
        patch.object(generate_video_covers, 'MP4', return_value=tags) as mp4:
      generate_video_covers.embed_mp4_cover('foo.mp4', 'foo.jpg')

    mp4.assert_called_once_with('foo.mp4')
    stored_cover = tags.__setitem__.call_args.args[1][0]
    self.assertEqual(stored_cover, cover_data)
    self.assertEqual(stored_cover.imageformat, generate_video_covers.MP4Cover.FORMAT_JPEG)
    tags.save.assert_called_once_with()

  def test_embeds_cover_in_asf_picture_tag(self):
    tags = MagicMock()
    cover_data = b'cover image'
    asf_picture = object()

    with patch.object(generate_video_covers, 'read_file', return_value=cover_data), \
        patch.object(generate_video_covers, 'ASF', return_value=tags) as asf, \
        patch.object(generate_video_covers, 'ASFByteArrayAttribute', return_value=asf_picture) as picture:
      generate_video_covers.embed_asf_cover('foo.wmv', 'foo.jpg')

    asf.assert_called_once_with('foo.wmv')
    picture.assert_called_once_with(cover_data)
    tags.__setitem__.assert_called_once_with('WM/Picture', [asf_picture])
    tags.save.assert_called_once_with()

if __name__ == '__main__':
  unittest.main()
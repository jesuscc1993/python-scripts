import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from extract_subs import find_subtitle_stream

class TestExtractSubs(unittest.TestCase):
  def test_finds_stream_when_metadata_contains_invalid_bytes(self):
    output = (
      b'{"streams":[{"codec_type":"subtitle","codec_name":"subrip",'
      b'"index":2,"tags":{"language":"eng","title":"foo \xff"}}]}'
    )

    def run_ffprobe(command, **kwargs):
      stdout = output.decode(kwargs['encoding'], errors = kwargs['errors'])
      return SimpleNamespace(stdout = stdout)

    with patch('extract_subs.subprocess.run', side_effect = run_ffprobe) as run:
      result = find_subtitle_stream('foo.mkv', 'eng')

    self.assertEqual(result, (2, 'subrip'))
    self.assertEqual(run.call_args.kwargs['encoding'], 'utf-8')
    self.assertEqual(run.call_args.kwargs['errors'], 'replace')

if __name__ == '__main__':
  unittest.main()
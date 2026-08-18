import os
import sys

from mtlogger import logger
from mtprompt import Prompt
from yt_dlp import YoutubeDL

YTDL_OPTIONS = {
  'format': 'bestaudio/best',
  'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3'
  }]
}

def main():
  youtube_url = sys.argv[1] if len(sys.argv) > 1 else Prompt.str('Enter a YouTube video/playlist URL/ID')
  output_dir_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), 'output')

  download_from_yt(output_dir_path, youtube_url)

def download_from_yt(
  output_dir_path: str,
  youtube_url: str,
):
  try:
    with YoutubeDL({
      **YTDL_OPTIONS,
      'outtmpl': os.path.join(output_dir_path, '%(title)s.%(ext)s')
    }) as ydl:
      ydl.download([youtube_url])
      logger.success('Download complete.')
  except Exception as ex:
    logger.error(f'Download failed: {ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

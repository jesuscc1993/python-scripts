import os
import sys

from mtlogger import logger
from yt_dlp import YoutubeDL

YTDL_OPTIONS = {
  'format': 'bestaudio/best',
  'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3'
  }]
}

def main():
  youtube_url = sys.argv[1] if len(sys.argv) > 1 else prompt_url()
  output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), 'output')

  download_from_yt(output_path, youtube_url)

def prompt_url():
  return input('Enter a YouTube video/playlist URL/ID: ').strip()

def download_from_yt(output_path, youtube_url):
  try:
    with YoutubeDL({
      **YTDL_OPTIONS,
      'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
    }) as ydl:
      ydl.download([youtube_url])
      print('Download complete.')
  except Exception as e:
    logger.error(f'Download failed: {e}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

import os
import sys

from mtlogger import logger
from spotdl import Spotdl
from spotdl.utils.search import parse_query

def main():
  spotify_url = sys.argv[1] if len(sys.argv) > 1 else prompt_url()
  output_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), 'output')

  download_from_spotify(output_path, spotify_url)

def prompt_url():
  return input('Enter a Spotify track/album/playlist URL: ').strip()

def download_from_spotify(output_path, spotify_url):
  try:
    spotdl = init_spotify_client(output_path)
    queries = parse_query(spotify_url)
    for query in queries:
      spotdl.download(query)
    print('Download complete.')
  except Exception as e:
    logger.error(f'Download failed: {e}')

def init_spotify_client(output_path):
  client_id = os.environ.get('SPOTIPY_CLIENT_ID')
  client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
  if not client_id or not client_secret:
    raise RuntimeError('SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables must be set.')

  return Spotdl(
    client_id = client_id,
    client_secret = client_secret,
    downloader_settings = { "output": output_path }
  )

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.error(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

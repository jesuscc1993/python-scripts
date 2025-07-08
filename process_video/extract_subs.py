import os
import subprocess
import sys

SUBTITLES_PATH = 'subtitles'
VIDEO_EXTS = ['.mp4', '.mkv']
SUBTITLE_EXT = '.srt'

def main():
  if len(sys.argv) > 1:
    dir_path = sys.argv[1]
  else:
    dir_path = prompt_path('Enter the path containing the videos to process:\n')

  process_directory(dir_path)

def process_directory(dir_path):
  output_path = os.path.join(dir_path, SUBTITLES_PATH)
  os.makedirs(output_path, exist_ok = True)

  for file_name in os.listdir(dir_path):
    name, ext = os.path.splitext(file_name)
    if ext.lower() in VIDEO_EXTS:
      src_file_path = os.path.join(dir_path, file_name)
      dest_file_path = os.path.join(output_path, name + SUBTITLE_EXT)
      cmd = [
        'ffmpeg',
        '-i', src_file_path,
        '-map', '0:s:0',
        dest_file_path
      ]
      subprocess.run(cmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

      if os.path.exists(dest_file_path) and os.path.getsize(dest_file_path) == 0:
        os.remove(dest_file_path)
        print(f'No subtitles found for "{file_name}". Removed empty subtitle file.')
      else:
        print(f'Extracted subtitles for "{file_name}".')

def prompt_path(prompt_message, optional = False):
  path = input(prompt_message).strip(' "\'')
  if not path or not os.path.isdir(path):
    print(f'The specified path "{path}" is not a directory.')
    if not optional: sys.exit(1)
    return None
  print('')
  return path

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

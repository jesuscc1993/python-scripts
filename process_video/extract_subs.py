import os
import subprocess
import sys

SUBTITLES_PATH = 'subtitles'
VIDEO_EXTS = ['.mp4', '.mkv']

def main():
  if len(sys.argv) > 1:
    dir_path = sys.argv[1]
  else:
    dir_path = prompt_path('Enter the path containing the videos to process:\n')

  process_directory(dir_path)

def process_directory(dir_path):
  os.makedirs(os.path.join(dir_path, SUBTITLES_PATH), exist_ok = True)

  for filename in os.listdir(dir_path):
    name, ext = os.path.splitext(filename)
    if ext.lower() in VIDEO_EXTS:
      input_path = os.path.join(dir_path, filename)
      output_path = os.path.join(dir_path, SUBTITLES_PATH, name + '.srt')
      cmd = [
        'ffmpeg',
        '-i', input_path,
        '-map', '0:s:0',
        output_path
      ]
      subprocess.run(cmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

      if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
        os.remove(output_path)
        print(f'No subtitles found for "{filename}". Removed empty subtitle file.')
      else:
        print(f'Extracted subtitles for "{filename}".')

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

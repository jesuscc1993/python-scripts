import os
import subprocess
import sys

from mtlogger import logger
from mtprompt import Prompt, to_path
from send2trash import send2trash

from _common import post_process_subs_file
from _constants import SUBTITLE_EXTS, SRT_EXT

def main():
	if len(sys.argv) > 1:
		input_path = to_path(sys.argv[1])
	else:
		input_path = Prompt.path('Enter the path to a subtitle file or directory')

	logger.log(f'Converting subtitles to SRT in "{input_path}"...')
	logger.hr()

	if os.path.isfile(input_path):
		process_file(input_path)
	elif os.path.isdir(input_path):
		process_directory(input_path)
	else:
		raise FileNotFoundError(f'Path does not exist: "{input_path}"')

	logger.hr()
	logger.log(f'Finished converting subtitles in "{input_path}".')

def process_directory(
	dir_path: str,
):
	for root, _, file_names in os.walk(dir_path):
		for file_name in file_names:
			process_file(os.path.join(root, file_name))

def process_file(
	file_path: str,
):
	ext = os.path.splitext(file_path)[1].lower()
	if ext not in SUBTITLE_EXTS or ext == SRT_EXT:
		return

	output_file_path = os.path.splitext(file_path)[0] + SRT_EXT
	convert_to_srt(file_path, output_file_path)

def convert_to_srt(
	input_file_path: str,
	output_file_path: str,
) -> bool:
	if os.path.exists(output_file_path):
		logger.warn(f'Skipping "{input_file_path}". Output already exists: "{output_file_path}".')
		return False

	result = subprocess.run(
		[
			'ffmpeg',
			'-v', 'error',
			'-n',
			'-i', input_file_path,
			'-c:s', 'srt',
			output_file_path
		],
    capture_output = True,
    encoding = 'utf-8',
    errors = 'replace',
    text = True,
	)

	if result.returncode != 0 or not os.path.isfile(output_file_path) or os.path.getsize(output_file_path) == 0:
		if os.path.exists(output_file_path):
			os.remove(output_file_path)
		error_message = result.stderr.strip() or 'ffmpeg did not create a non-empty SRT file.'
		logger.warn(f'Failed to convert "{input_file_path}": {error_message}')
		return False

	post_process_subs_file(output_file_path, SRT_EXT)
	logger.success(f'Converted "{input_file_path}" to "{output_file_path}".')
	send2trash(input_file_path)
	return True

if __name__ == '__main__':
	try:
		main()
	except Exception as ex:
		logger.unhandled_error(ex)

	Prompt.enter_to_exit()
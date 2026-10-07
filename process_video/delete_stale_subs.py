import os
import sys

from send2trash import send2trash
from mtlogger import logger
from mtprompt import Prompt, to_path

from _constants import SUBTITLE_EXTS, VIDEO_EXTS

SUBTITLES_PATHS = {'subs', 'subtitles'}

def main():
	if len(sys.argv) > 1:
		input_path = to_path(sys.argv[1])
	else:
		input_path = Prompt.dir(
			'Enter the path to the directory containing your video files'
    )

	logger.log(f'Deleting stale subtitles in "{input_path}"...')
	logger.hr()

	delete_stale_subtitle_files(input_path)

	logger.hr()
	logger.log(f'Finished deleting stale subtitles in "{input_path}".')

def find_stale_subtitle_files(
	dir_path: str,
) -> list[str]:
	video_stems_by_dir = {}
	subtitle_files = []

	for root, _, file_names in os.walk(dir_path):
		video_stems_by_dir[root] = {
			os.path.splitext(file_name)[0].casefold()
			for file_name in file_names
			if os.path.splitext(file_name)[1].lower() in VIDEO_EXTS
		}

		subtitle_files.extend(
			os.path.join(root, file_name)
			for file_name in file_names
			if os.path.splitext(file_name)[1].lower() in SUBTITLE_EXTS
		)

	stale_files = []
	for file_path in subtitle_files:
		subtitle_dir = os.path.dirname(file_path)
		if os.path.basename(subtitle_dir).casefold() in SUBTITLES_PATHS:
			video_dir = os.path.dirname(subtitle_dir)
		else:
			video_dir = subtitle_dir

		video_stems = video_stems_by_dir.get(video_dir, set())
		subtitle_stem = os.path.splitext(os.path.basename(file_path))[0].casefold()
		if subtitle_stem not in video_stems:
			stale_files.append(file_path)

	return stale_files

def delete_stale_subtitle_files(
	dir_path: str,
):
	stale_files = find_stale_subtitle_files(dir_path)
	if not stale_files:
		logger.log('No stale subtitles were found.')
		return

	for file_path in stale_files:
		send2trash(file_path)
		logger.log(f'Moved "{file_path}" to the Recycle Bin.')

	logger.success(f'Moved {len(stale_files)} stale subtitle files to the Recycle Bin.')

if __name__ == '__main__':
	try:
		main()
	except Exception as ex:
		logger.unhandled_error(ex)

	Prompt.enter_to_exit()

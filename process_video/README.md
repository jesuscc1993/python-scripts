# Process Video

## Description

Collection of scripts for processing video files and subtitles.

## Scripts

### [extract_subs.py](extract_subs.py)

Extracts embedded subtitle tracks from video files as `.srt`.

### [generate_video_covers.py](generate_video_covers.py)

Generates a cover image for each video, overlaying its runtime/resolution.

### [postprocess_subs.py](postprocess_subs.py)

Fixes invalid characters, adds missing spaces and strips tags from `.srt` files.

### [delete_stale_subs.py](delete_stale_subs.py)

Moves subtitle files to the Recycle Bin when no same-name `.mp4` or `.mkv` video exists beside them. Also checks subtitle files in a `subs` or `subtitles` subfolder against videos in its parent folder.

### [convert_to_srt.py](convert_to_srt.py)

Converts supported non-SRT subtitle files to `.srt` with FFmpeg and moves the original to the Recycle Bin after successful conversion. Existing `.srt` files are not overwritten.

### [shift_subs.py](shift_subs.py)

Shifts every timestamp in an `.srt` file by a given amount of milliseconds.

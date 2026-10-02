# Process Manga

## Description

Iterates manga folders and images to resize them if larger than a particular target device.<br>
Will also convert non-JPG files to JPG.

## Specific Requirements

- `upscale_manga.py`
  - Download your waifu2x client of choice to /waifu2x
  - Rename the exe to `waifu2x.exe`
  - Rename the model name in `upscale_manga.py` to match the one bundled with your exe

## Individual Scripts

### [compare_dirs.py](compare_dirs.py)

Compares two folders and reports the volume/chapter differences between them.

### [compress_folders.py](compress_folders.py)

Runs `../compress/compress_folders`, then `rename_items`.

### [compress_subfolders.py](compress_subfolders.py)

Runs `../compress/compress_subfolders`, then `rename_items`.

### [copy_metadata_files.py](copy_metadata_files.py)

Copies `ComicInfo.xml` / `cover.jpg` / `desktop.ini` / `icon.ico` and the hidden marker files between matching folders.

### [crop_borders.py](crop_borders.py)

Crops uniform-colored borders from manga page images.

### [crop_webtoon.py](crop_webtoon.py)

Crops a tall webtoon strip image into separate manga-sized pages.

### [delete_image_matches.py](delete_image_matches.py)

Deletes images that are near-duplicates of each other, based on perceptual hashing.

### [download_from_site.py](download_from_site.py)

Downloads manga chapter images from a URL pattern.

### [generate_metadata.py](generate_metadata.py)

Searches MyAnimeList and generates a `ComicInfo.xml` + `cover.jpg` for each manga folder.

### [merge_volumes.py](merge_volumes.py)

Merges chapter folders into their corresponding volume folders.

### [prefix_volumes.py](prefix_volumes.py)

Prefixes chapter files/folders with their volume number.

### [rename_items.py](rename_items.py)

Renames chapter/volume items to a normalized name format.

### [resize_manga.py](resize_manga.py)

Resizes manga page images if larger than a particular target device, converting non-JPG files to JPG.

### [shift_monochrome_levels.py](shift_monochrome_levels.py)

Shifts the black/white levels of monochrome manga page images.

### [upscale_manga.py](upscale_manga.py)

Upscales manga page images using a waifu2x client.

### [validate_chapters.py](validate_chapters.py)

Validates that chapter numbers are sequential and continuous within a folder.

### Chaining Scripts

Each runs a sequence of individual scripts:

### [chain_process_manga.py](chain_process_manga.py)

Runs `merge_volumes` > `crop_borders` > `compress_folders` (ZIP) > `rename_items` > `../rename/rename_zip_to_cbz`.

### [chain_process_volumes.py](chain_process_volumes.py)

Runs `extract_archives` > `prefix_volumes` > `merge_volumes` > `compress_folders` (ZIP) > `rename_items` > `../rename/rename_zip_to_cbz`.

### [chain_process_webtoon.py](chain_process_webtoon.py)

Runs `crop_webtoon` > `compress_folders` (ZIP) > `rename_items`.

### [chain_reprocess_manga.py](chain_reprocess_manga.py)

Runs `extract_archives` > `resize_manga` > `compress_folders` (ZIP) > `rename_items` > `../rename/rename_zip_to_cbz`.

### [chain_reprocess_webtoon.py](chain_reprocess_webtoon.py)

Runs `extract_archives` > `crop_webtoon` > `compress_folders` (ZIP) > `rename_items`.

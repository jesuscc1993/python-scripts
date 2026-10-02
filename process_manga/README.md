# Process Manga

## Description

Iterates manga folders and images to resize them if larger than a particular target device.<br>
Will also convert non-JPG files to JPG.

## Specific Requirements

- `upscale_manga.py`
  - Download your waifu2x client of choice to /waifu2x
  - Rename the exe to `waifu2x.exe`
  - Rename the model name in `upscale_manga.py` to match the one bundled with your exe

## Scripts

### Chains

Each of these runs a sequence of the individual scripts below, in order:

- `chain_process_manga`: `merge_volumes` > `crop_borders` > `compress_folders` (ZIP) > `rename_items` > `rename_zip_to_cbz`
- `chain_process_volumes`: `extract_archives` > `prefix_volumes` > `merge_volumes` > `compress_folders` (ZIP) > `rename_items` > `rename_zip_to_cbz`
- `chain_process_webtoon`: `crop_webtoon` > `compress_folders` (ZIP) > `rename_items`
- `chain_reprocess_manga`: `extract_archives` > `resize_manga` > `compress_folders` (ZIP) > `rename_items` > `rename_zip_to_cbz`
- `chain_reprocess_webtoon`: `extract_archives` > `crop_webtoon` > `compress_folders` (ZIP) > `rename_items`

### Individual

- `compare_dirs`: Compares two folders and reports the volume/chapter differences between them.
- `compress_folders`: Runs `../compress/compress_folders`, then `rename_items`.
- `compress_subfolders`: Runs `../compress/compress_subfolders`, then `rename_items`.
- `copy_metadata_files`: Copies `ComicInfo.xml` / `cover.jpg` / `desktop.ini` / `icon.ico` and the hidden marker files between matching folders.
- `crop_borders`: Crops uniform-colored borders from manga page images.
- `crop_webtoon`: Crops a tall webtoon strip image into separate manga-sized pages.
- `delete_image_matches`: Deletes images that are near-duplicates of each other, based on perceptual hashing.
- `download_from_site`: Downloads manga chapter images from a URL pattern.
- `generate_metadata`: Searches MyAnimeList and generates a `ComicInfo.xml` + `cover.jpg` for each manga folder.
- `merge_volumes`: Merges chapter folders into their corresponding volume folders.
- `overlay_cover_score`: Overlays the MAL score onto each folder's cover image.
- `prefix_volumes`: Prefixes chapter files/folders with their volume number.
- `rename_items`: Renames chapter/volume items to a normalized name format.
- `resize_manga`: Resizes manga page images if larger than a particular target device, converting non-JPG files to JPG.
- `shift_monochrome_levels`: Shifts the black/white levels of monochrome manga page images.
- `suffix_score`: Searches MyAnimeList and appends the score to the end of each manga folder's name.
- `upscale_manga`: Upscales manga page images using a waifu2x client.
- `validate_chapters`: Validates that chapter numbers are sequential and continuous within a folder.

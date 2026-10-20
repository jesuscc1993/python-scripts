# Rename

## Description

Collection of scripts for renaming files and folders sequentially or by pattern.

## Scripts

### [rename_files_sequentially.py](rename_files_sequentially.py)

Iterates direct child files inside a specified folder and renames them sequentially.
Child directories are not affected.
Useful to get consecutively named items when some are missing (e.g. 1,2,6 > 1,2,3).

### [rename_subfolders_sequentially.py](rename_subfolders_sequentially.py)

Mirrors the script above, except targeting directories intsead of files.

### [rename_subfolders_files_sequentially.py](rename_subfolders_files_sequentially.py)

Iterates direct child files inside direct subfolders a specified folder and renames them sequentially.

### [rename_zip_to_cbz.py](rename_zip_to_cbz.py)

Recursively renames `.zip` files to `.cbz`.

### [wrap_in_spaces.py](wrap_in_spaces.py)

Wraps a file/directory in `U+00A0` spaces, putting them at the top when sorting.

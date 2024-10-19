# Folder Icon Generator

## Description

Python script that generates folder icons for each folder.<br>
Each different script will generate these icons from different sources.<br>
Windows only.

## Requirements

- Having python installed.
- Running `pip install -r requirements.txt` to install the required dependencies.

#### Running

- Run `SCRIPT_NAME.py`.
- Run `python SCRIPT_NAME.py` in the terminal.

(replace SCRIPT_NAME with your script of choice)

### generate-icons-from-folder-images

Will look for `folder.jpg` / `cover.jpg` / `AlbumArtSmall.jpg` files inside the folder.

### generate-ps-save-icons

Will look for `ICON0.PNG` files inside the folder.<br>
Only compatible with PSP and PS3 saves, which are the only save types that include an unpacked image alongside saves.

## Notes

The OS will only load up the icons when it feels like it; it usually seems to be at random.<br>
There are some workarounds but they only sometimes work.<br>
Often the best bet is to sign out or restart the computer, but even this is unreliable.

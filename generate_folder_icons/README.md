# Generate Folder Icons

## Description

Iterates folders and generates icons for each one.<br>
Each different script will generate these icons from different sources.<br>
<strong>Windows only.</strong>

## Scripts

### [generate_icons_from_all_images.py](generate_icons_from_all_images.py)

Will generate an icon from every image found inside the folder.

### [generate_icons_from_exes.py](generate_icons_from_exes.py)

Will generate an icon from the first non-blacklisted `.exe` found inside the folder.

### [generate_icons_from_folder_images.py](generate_icons_from_folder_images.py)

Will look for `folder.jpg` / `cover.jpg` / `AlbumArtSmall.jpg` files inside the folder.

### [generate_ps_save_icons.py](generate_ps_save_icons.py)

Will look for `ICON0.PNG` files inside the folder.<br>
Only compatible with PSP and PS3 saves, which are the only save types that include an unpacked image alongside saves.

### [overlay_icons_with_file_size.py](overlay_icons_with_file_size.py)

Overlays the folder's size in GB onto its existing icon.

## Notes

The OS will only load up the icons when it feels like it; it usually seems to be at random.<br>
There are some workarounds but they only sometimes work.<br>
Often the best bet is to sign out or restart the computer, but even this is unreliable.

# Generate Folder Images

## Description

Iterates folders and generates folder.jpg for each one.<br>
Each different script will generate these images from different sources.<br>

## Scripts

### [generate_igdb_folder_images.py](generate_igdb_folder_images.py)

Looks up each folder's name on IGDB and downloads its cover image.<br>
Make sure to set up the following ENV keys:
TWITCH_CLIENT_ID
TWITCH_CLIENT_SECRET

### [generate_ps3_folder_images.py](generate_ps3_folder_images.py)

Looks up each folder's game ID on RPCS3's wiki and downloads its cover image.

### [generate_ps4_folder_images.py](generate_ps4_folder_images.py)

Looks up each folder's game ID on SerialStation and downloads its cover image.

### [generate_ps_save_folder_images.py](generate_ps_save_folder_images.py)

Looks for `ICON0.PNG` files inside the folder.

### [generate_psp_folder_images.py](generate_psp_folder_images.py)

Looks up each folder's game ID on CDRomance and downloads its cover image.

### [generate_steam_folder_images.py](generate_steam_folder_images.py)

Downloads each folder's Steam capsule image, matched by app ID.

### [generate_switch_folder_images.py](generate_switch_folder_images.py)

Looks up each folder's title ID against Nintendo Switch's title database and downloads its icon.

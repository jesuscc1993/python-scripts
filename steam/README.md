# Steam

## Description

Various scripts for interacting with Steam.

## Common

### For features that use the API, you will need to create a `.env` file and define the following variables:

#### Required

STEAM_API_KEY
STEAM_USER_ID3
STEAM_USER_ID64
STEAM_INSTALL_PATH

#### Optional

COVER_H
COVER_W
HEADER_H
HEADER_W

## Scripts

### [add_non_steam_game.py](add_non_steam_game.py)

Adds a non-Steam game shortcut (`.exe` / `.lnk` / `.url`) to Steam.

### [download_game_assets.py](download_game_assets.py)

Searches the Steam store for a game and downloads its cover/header/icon assets.

### [export_owned_steam_app_ids.py](export_owned_steam_app_ids.py)

Exports the app IDs of every game you own to a JSON file.

### [export_wishlist.py](export_wishlist.py)

Exports your Steam wishlist to a JSON file.

### [generate_steam_app_manifests.py](generate_steam_app_manifests.py)

Generates an `appmanifest_{app_id}.acf` file for each game folder, matched against your owned games.

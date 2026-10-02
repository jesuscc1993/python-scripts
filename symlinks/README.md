# Symlinks

## Description

Collection of scripts for creating symlinks.<br>
<strong>Windows only.</strong>

## Instructions

### ENV

Most scripts will read values from ENV. You can either declare them on your OS or add an .en file containing them.
These are the different keys the scripts may look for:

GAME_SAVES_PATH

STEAM_USER_ID3
STEAM_USER_ID64
STEAM_USER_ID64H
EPIC_USER_ID
UBISOFT_USER_ID
GAME_CLIENTS_SAVES_PATH

ROMS_PATH
EMULATORS_PATH
EMULATORS_SAVE_PATH
TEXTURE_PACKS_PATH

SPECIFIC_GAME_SAVES_PATH

You can use [https://www.steamidfinder.com](https://www.steamidfinder.com) to find your Steam ID in the different formats.

### Scripts

All scripts require admin privileges.

- `mklink_emulators`: Links emulator save/config folders (Citra/3DS, Dolphin/Wii-GCN, Switch, texture packs) to `EMULATORS_PATH` / `EMULATORS_SAVE_PATH` / `TEXTURE_PACKS_PATH`.
- `mklink_game_clients`: Links game client install/save folders (Epic, Steam, Ubisoft) to `GAME_CLIENTS_SAVES_PATH`.
- `mklink_general_game_saves`: Links general (non-client-specific) game save folders to `GAME_SAVES_PATH`.
- `mklink_hidden`: Renames an item and recreates it as a hidden symlink under its original name.
- `mklink_replace`: Backs up files containing a "link token" and replaces them with symlinks to their "target token" counterpart.
- `mklink_specific_game_saves`: See [Specific Game Saves](#specific-game-saves) below.
- `mklink_themes_and_skins`: Links Rainmeter and Steam theme/skin folders.

### Specific Game Saves

To use [mklink_specific_game_saves.py](mklink_specific_game_saves.py), you will additionally need to create a specific_mappings.json containing a mapping in the following format:

```
[
  {
    "path_prefix": str,
    "items": [
      {
        "src": str,
        "dest": str,
        "expand": bool, // create folder if it does not exist (default: true)
        "isFile": bool // is link a file? (default: false)
      }
    ]
  }
]

```

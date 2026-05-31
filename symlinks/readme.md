## Instructions

### ENV

Most scripts will read values from ENV. You can either declare them on your OS or add an .en file containing them.
These are the different keys the scripts may look for:

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

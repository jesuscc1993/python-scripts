## Common

### For features that use the API, you will need to create a `.env` file and define the following variables:

#### Required

STEAM_API_KEY
STEAM_USER_ID3
STEAM_INSTALL_PATH

#### Optional

COVER_H
COVER_W
HEADER_H
HEADER_W

## Generate Steam Covers

### Description

Iterates existing Steam save folders and opens the store page for each on a new browser tab.

### Requirements

- Having python installed.
- Running `pip install -r requirements.txt` to install the required dependencies.

### Running

- Run `generate_steam_covers.py`.
- Run `python generate_steam_covers.py` in the terminal.

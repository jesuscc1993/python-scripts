import os

DIR_BLACKLIST = ['__InstallData__']
EMPTY_CELL = '<span class="dim">N/A</span>'
GENERIC_EXCLUSION_FILE = '.noscan'
STYLE = 'th { text-align: center !important; } .dim { filter: brightness(0.5); } .justify-between { display:flex; justify-content:space-between; gap: 0.25em; }'

GAME_DIRS_SCAN_TYPE = 'game_dirs'
WISHLIST_FILE_SCAN_TYPE = 'wishlist_file'

COMPACT_GUI_EXCLUSION_FILE = '.nocompactguiscan'

HLTB_DB_NAME = 'hltb_database.json'
HLTB_EXCLUSION_FILE = '.nohltbscan'
HLTB_OUTPUT_DIRNAME = 'hltb'

DATA_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '_data')
OUTPUT_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '_output')
HLTB_DB_PATH = os.path.join(DATA_DIR_PATH, HLTB_DB_NAME)

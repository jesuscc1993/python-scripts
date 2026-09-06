import os

DIR_BLACKLIST = ['__InstallData__']
EMPTY_CELL = 'N/A'
GENERIC_EXCLUSION_FILE = '.noscan'
HLTB_DB_NAME = 'hltb_database.json'
HLTB_EXCLUSION_FILE = '.nohltbscan'
HLTB_OUTPUT_DIRNAME = 'hltb'
STYLE = 'th { text-align: center !important; } .dim { filter: brightness(0.5); } .justify-between { display:flex; justify-content:space-between; gap: 0.25em; }'

DATA_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '_data')
OUTPUT_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '_output')
HLTB_DB_PATH = os.path.join(DATA_DIR_PATH, HLTB_DB_NAME)

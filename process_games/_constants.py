import os

DIR_BLACKLIST = ['__InstallData__']
EMPTY_CELL = 'N/A'
GENERIC_EXCLUSION_FILE = '.noscan'
STYLE = 'th { text-align: center !important; } .dim { filter: brightness(0.5); } .justify-between { display:flex; justify-content:space-between; gap: 0.25em; }'

HLTB_DB_NAME = 'hltb_database.json'
HLTB_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '_data', HLTB_DB_NAME)

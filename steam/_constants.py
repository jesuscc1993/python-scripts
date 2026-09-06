import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

OUTPUT_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '_output', 'steam')
REQUEST_TIMEOUT = 30

STEAM_API_KEY = os.environ.get('STEAM_API_KEY')
STEAM_INSTALL_PATH = os.environ.get('STEAM_INSTALL_PATH')
STEAM_USER_ID3 = os.environ.get('STEAM_USER_ID3')
STEAM_USER_ID64 = os.environ.get('STEAM_USER_ID64')

COVER_H = os.environ.get('COVER_H')
COVER_W = os.environ.get('COVER_W')
HEADER_H = os.environ.get('HEADER_H')
HEADER_W = os.environ.get('HEADER_W')

COVER_H = int(COVER_H) if COVER_H else None
COVER_W = int(COVER_W) if COVER_W else None
HEADER_H = int(HEADER_H) if HEADER_H else None
HEADER_W = int(HEADER_W) if HEADER_W else None

GET_OWNED_GAMES_ENDPOINT_URL = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/'
GET_WISHLIST_ENDPOINT_URL = 'https://api.steampowered.com/IWishlistService/GetWishlist/v1/'
GET_WISHLIST_SORTED_FILTERED_ENDPOINT_URL = 'https://api.steampowered.com/IWishlistService/GetWishlistSortedFiltered/v1/'

COVER_URL_MAP = {
	'header': {
		'url': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/header.jpg',
		'dest': '{}.jpg',
		'size': [HEADER_W, HEADER_H] if HEADER_W and HEADER_H else None
	},
	'library': {
		'url': 'https://steamcdn-a.akamaihd.net/steam/apps/{}/library_600x900_2x.jpg',
		'dest': '{}p.jpg',
		'size': [COVER_W, COVER_H] if COVER_W and COVER_H else None
	}
}

HEADER_SIZE = COVER_URL_MAP['header']['size']
COVER_SIZE = COVER_URL_MAP['library']['size']

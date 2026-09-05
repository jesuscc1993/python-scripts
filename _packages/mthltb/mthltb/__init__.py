import re
import requests
import unicodedata

from typing import Optional, TypedDict

HLTB_SEARCH_URL = 'https://howlongtobeat.com/api/search/site'
HLTB_GAME_URL = 'https://howlongtobeat.com/game/{}'
HLTB_SEARCH_QUERY_URL = 'https://howlongtobeat.com/?q={}'
REQUEST_TIMEOUT = 10

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

class HltbResult(TypedDict):
  game_id: int
  game_name: str
  comp_main: Optional[int]
  comp_plus: Optional[int]
  comp_100: Optional[int]
  url: str

class Hltb:

  @staticmethod
  def search(
    game_name: str,
  ) -> Optional[HltbResult]:
    token, hp_key, hp_val = get_token()

    response = requests.post(
      HLTB_SEARCH_URL,
      json = build_query(normalize_game_name(game_name), hp_key, hp_val),
      headers = build_headers(token, hp_key, hp_val),
      timeout = REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    entries = response.json().get('data') or []
    if not entries:
      return None

    entry = next(
      (entry for entry in entries if entry.get('game_name', '').lower() == game_name.lower()),
      entries[0]
    )

    game_id = entry.get('game_id')
    return {
      **entry,
      'game_id': game_id,
      'url': HLTB_GAME_URL.format(game_id) if game_id else HLTB_SEARCH_QUERY_URL.format(game_name),
    }

def get_token():
  response = requests.get(
    f'{HLTB_SEARCH_URL}/init?t=',
    headers = {
      'Accept': '*/*',
      'Referer': 'https://howlongtobeat.com/?q=',
      'User-Agent': USER_AGENT,
    },
    timeout = REQUEST_TIMEOUT,
  )
  response.raise_for_status()

  data = response.json()
  return data.get('token'), data.get('hpKey'), data.get('hpVal')

def build_query(
  normalized_name: str,
  hp_key: str,
  hp_val: str,
):
  return {
    'searchType': 'games',
    'searchTerms': normalized_name.split(),
    'searchPage': 1,
    'size': 20,
    'searchOptions': {
      'games': {
        'userId': 0,
        'platform': '',
        'sortCategory': 'popular',
        'rangeCategory': 'main',
        'rangeTime': { 'min': None, 'max': None },
        'gameplay': { 'perspective': '', 'flow': '', 'genre': '', 'difficulty': '' },
        'rangeYear': { 'min': '', 'max': '' },
        'modifier': '',
      },
      'users': { 'sortCategory': 'postcount' },
      'lists': { 'sortCategory': 'follows' },
      'filter': '',
      'sort': 0,
      'randomizer': 0,
    },
    'useCache': False,
    hp_key: hp_val,
  }

def build_headers(
  token: str,
  hp_key: str,
  hp_val: str,
):
  return {
    'Content-Type': 'application/json',
    'Origin': 'https://howlongtobeat.com',
    'Referer': 'https://howlongtobeat.com/',
    'User-Agent': USER_AGENT,
    'x-auth-token': token,
    'x-hp-key': hp_key,
    'x-hp-val': hp_val,
  }

def normalize_game_name(
  name: str,
):
  normalized = unicodedata.normalize('NFD', name)
  normalized = re.sub(r'[\u0300-\u036f]', '', normalized)
  normalized = normalized.replace('’', "'")
  normalized = re.sub(r"[^a-z _0-9`~!@#$%^&*()_=+|\\\]}[{;:',<.>/?]", '', normalized, flags = re.IGNORECASE)
  return normalized

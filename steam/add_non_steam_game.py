import argparse
import binascii
import json
import os
import time

from mtlogger import logger
from mtprompt import Prompt
from pathlib import Path

from _common import download_assets_for_app_id

STEAM_USER_ID3 = os.environ.get('STEAM_USER_ID3')
STEAM_INSTALL_PATH = os.environ.get('STEAM_INSTALL_PATH')

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'vdf_game_template.json')

TYPE_NONE = 0x00
TYPE_STRING = 0x01
TYPE_INT = 0x02
TYPE_END = 0x08

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-appid', required = False, type = int)
  parser.add_argument('-appname', required = False)
  parser.add_argument('-exe', required = False)
  parser.add_argument('-icon', required = False)
  args = parser.parse_args()

  exe, app_name, icon, app_id = args.exe, args.appname, args.icon, args.appid
  if not exe:
    exe = Prompt.str('Enter the path to the exe')
    app_name = Prompt.str('Enter the app name (optional)', default = Path(exe).stem)
    icon = Prompt.str('Enter the path to the icon (optional)', default = exe)
    app_id = Prompt.int('Enter the Steam app id (optional)', default = None)

  path = Path(STEAM_INSTALL_PATH, 'userdata', STEAM_USER_ID3, 'config', 'shortcuts.vdf')
  data = path.read_bytes()
  root, _ = parse_object(data)

  with open(TEMPLATE_PATH) as f:
    entry = json.load(f)

  inner = root.get('shortcuts', {})
  shortcut_appid = generate_app_id(exe)

  if any(g.get('appid') == shortcut_appid for g in inner.values()):
    logger.warn(f'Skipping "{exe}". Game is already present as appid {shortcut_appid}.')
    return

  entry['appid'] = shortcut_appid
  entry['appname'] = app_name or Path(exe).stem
  entry['Exe'] = exe
  entry['StartDir'] = str(Path(exe).parent)
  entry['icon'] = icon or exe

  inner[str(len(inner))] = entry
  root['shortcuts'] = inner

  serialized = serialize_object(root)
  bak_path = path.parent / f'{path.stem}.{int(time.time())}.bak'
  path.rename(bak_path)
  logger.debug(f'Saved backup "{bak_path}"')

  path.write_bytes(serialized)
  logger.success(f'Saved "{path}"')

  if app_id is not None:
    grid_path = Path(STEAM_INSTALL_PATH, 'userdata', STEAM_USER_ID3, 'config', 'grid')
    download_assets_for_app_id(app_id, grid_path, entry['appid'])

def generate_app_id(exe):
  key = exe.encode('utf-8')
  return binascii.crc32(key) | 0x80000000

def read_cstring(data, offset):
  end = data.index(b'\x00', offset)
  return data[offset:end].decode('utf-8'), end + 1

def parse_object(data, offset = 0):
  obj = {}

  while True:
    value_type = data[offset]
    offset += 1

    if value_type == TYPE_END:
      return obj, offset

    key, offset = read_cstring(data, offset)

    if value_type == TYPE_NONE:
      value, offset = parse_object(data, offset)
    elif value_type == TYPE_STRING:
      value, offset = read_cstring(data, offset)
    elif value_type == TYPE_INT:
      value = int.from_bytes(data[offset:offset + 4], 'little', signed = False)
      offset += 4
    else:
      raise ValueError(f'Unknown type: {value_type:#x}')

    obj[key] = value

def serialize_object(obj):
  result = bytearray()
  for key, value in obj.items():
    key_bytes = key.encode('utf-8') + b'\x00'
    if isinstance(value, dict):
      result += bytes([TYPE_NONE]) + key_bytes + serialize_object(value)
    elif isinstance(value, str):
      result += bytes([TYPE_STRING]) + key_bytes + value.encode('utf-8') + b'\x00'
    elif isinstance(value, int):
      result += bytes([TYPE_INT]) + key_bytes + (value & 0xFFFFFFFF).to_bytes(4, 'little')
    else:
      raise ValueError(f'Unsupported type: {type(value)}')
  result += bytes([TYPE_END])
  return bytes(result)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

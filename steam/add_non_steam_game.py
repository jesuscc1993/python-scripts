import argparse
import binascii
import configparser
import json
import os
import pythoncom
import time

from mtlogger import logger
from mtprompt import Prompt
from pathlib import Path
from pathlib import Path
from win32com.shell import shell # type: ignore

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
    exe = Prompt.str('Enter the path to the *.exe | *.lnk | *.url').strip('"')
    if exe.lower().endswith('.lnk') or exe.lower().endswith('.url'):
      info = get_shortcut_info(exe)
      exe = info['target']
      app_name = app_name or info['name']
      icon = icon or info['icon']

    app_name = app_name or Prompt.str('Enter the app name (optional)', default = Path(exe).stem)
    icon = icon or Prompt.str('Enter the path to the icon (optional)', default = exe)
    app_id = app_id or Prompt.int('Enter the Steam app id (optional)', optional = True)

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
  entry['StartDir'] = str(Path(exe).parent) if Path(exe).is_file() else ''
  entry['icon'] = icon or exe

  logger.debug(f'Generated entry:\n{stringify(entry)}\n')

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

def generate_app_id(
  exe_path: str,
):
  key = exe_path.encode('utf-8')
  return binascii.crc32(key) | 0x80000000

def read_cstring(
  data: bytes,
  offset: int,
):
  end = data.index(b'\x00', offset)
  return data[offset:end].decode('utf-8'), end + 1

def parse_object(
  data: bytes,
  offset = 0,
):
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

def serialize_object(
  obj: dict,
):
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

def get_shortcut_info(
  file_path: str,
):
  file_path = Path(file_path)

  match file_path.suffix.lower():
    case '.lnk':
      info = get_lnk_info(file_path)
    case '.url':
      info = get_url_info(file_path)
    case _:
      raise ValueError(f'Unsupported shortcut type: {file_path.suffix}')

  logger.debug(f'Parsed shortcut "{file_path}":\n{stringify(info)}\n')
  return info

def get_lnk_info(
  file_path: str,
):
  link = pythoncom.CoCreateInstance(
    shell.CLSID_ShellLink,
    None,
    pythoncom.CLSCTX_INPROC_SERVER,
    shell.IID_IShellLink
  )
  link.QueryInterface(pythoncom.IID_IPersistFile).Load(str(file_path))

  name = Path(file_path).stem
  target = link.GetPath(0)[0]
  icon, _ = link.GetIconLocation()
  icon = icon or target

  return {
    'name': name,
    'target': target,
    'icon': icon,
  }

def get_url_info(
  file_path: str,
):
  cfg = configparser.ConfigParser(interpolation = None)
  cfg.read(file_path, encoding = 'utf-8')
  shortcut = cfg['InternetShortcut']

  name = Path(file_path).stem
  target = shortcut.get('URL', '')
  icon = shortcut.get('IconFile', '') or target

  return {
    'icon': icon,
    'name': name,
    'target': target,
  }

def stringify(
  obj: dict,
):
  return json.dumps(obj, indent = 2)

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

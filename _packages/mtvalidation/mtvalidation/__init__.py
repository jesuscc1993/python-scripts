import os


def to_bool(val: str):
  val = val.strip().lower()

  if val in ('1', 'y', 'yes', 't', 'true'):
    return True
  if val in ('0', 'n', 'no', 'f', 'false'):
    return False

  raise ValueError(f'Value "{val}" is not a valid boolean (y/n).')


def to_int(val: str):
  val = val.strip()

  try:
    return int(val)
  except ValueError:
    raise ValueError(f'Input "{val}" is not an integer.')


def to_float(val: str):
  val = val.strip()

  try:
    return float(val)
  except ValueError:
    raise ValueError(f'Input "{val}" is not a valid number.')


def to_path(val: str):
  val = os.path.abspath(val.strip(' "'))

  if not os.path.exists(val):
    raise ValueError(f'Path "{val}" does not exist.')

  return val


def to_dir(val: str):
  val = os.path.abspath(val.strip(' "'))

  if not os.path.isdir(val):
    raise ValueError(f'Path "{val}" is not a directory.')

  return val


def to_file(val: str):
  val = os.path.abspath(val.strip(' "'))

  if not os.path.isfile(val):
    raise ValueError(f'Path "{val}" is not a file.')

  return val


def to_list(val: str):
  separator = '|' if '|' in val else ';' if ';' in val else ','
  return [_strip_quotes(item.strip()) for item in val.split(separator)]


def _strip_quotes(value: str):
  return (
    value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'")
    else value
  )

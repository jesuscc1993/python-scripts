import winreg

from mtlogger import logger

HKEY_NAMES = {
  winreg.HKEY_CLASSES_ROOT: 'HKEY_CLASSES_ROOT',
  winreg.HKEY_CURRENT_CONFIG: 'HKEY_CURRENT_CONFIG',
  winreg.HKEY_CURRENT_USER: 'HKEY_CURRENT_USER',
  winreg.HKEY_LOCAL_MACHINE: 'HKEY_LOCAL_MACHINE',
  winreg.HKEY_USERS: 'HKEY_USERS',
}

def add_registry_entry(root, path, name, value):
  try:
    with winreg.CreateKey(root, path) as key:
      winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
      logger.info(f' Set registry entry "{get_registry_key(root, path, name)}" with value "{value}"')
  except Exception as ex:
    logger.error(f'Could not add registry entry for "{get_registry_key(root, path)}": {ex}')

def delete_registry_entry(root, path, name = None):
  try:
    if not name:
      winreg.DeleteKey(root, path)
      logger.log(f'Deleted key: "{get_registry_key(root, path)}"')
    else:
      with winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE) as key:
        winreg.DeleteValue(key, name)
        logger.log(f'Deleted value: "{get_registry_key(root, path, name)}"')
  except FileNotFoundError:
    logger.warn(f' Could not find registry entry "{get_registry_key(root, path, name)}"')
  except Exception as ex:
    logger.error(f'Could not delete registry entry "{get_registry_key(root, path)}": {ex}')

def get_registry_value(root, path, name):
  try:
    with winreg.OpenKey(root, path) as key:
      return winreg.QueryValueEx(key, name)[0]
  except FileNotFoundError:
    return None
  except Exception as ex:
    logger.error(f'Could not get value for registry entry "{get_registry_key(root, path, name)}": {ex}')
    return None

def get_registry_key(root, path, name = None):
  root_name = HKEY_NAMES.get(root, str(root))
  return f'{root_name}\\{path}' + (f'\\{name}' if name else '')
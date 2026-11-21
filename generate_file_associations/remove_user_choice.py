import ctypes
import os
import sys
import winreg

from mtlogger import logger
from mtprompt import Prompt

from _registry import delete_registry_entry

FILE_EXTS = 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts'
USER_CHOICE_KEYS = ['UserChoice', 'UserChoiceLatest']


def run_as_admin():
  if os.name == 'nt' and not ctypes.windll.shell32.IsUserAnAdmin():
    params = ' '.join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(
      None, 'runas', sys.executable, params, None, 1
    )
    sys.exit(0)


def main():
  run_as_admin()

  ext = Prompt.str(
    'Enter the extension you want to remove user choice from'
  ).replace('.', '')

  for key in USER_CHOICE_KEYS:
    delete_registry_entry(
      winreg.HKEY_CURRENT_USER, f'{FILE_EXTS}\\.{ext}\\{key}'
    )


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

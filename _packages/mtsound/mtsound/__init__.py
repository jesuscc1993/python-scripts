import contextlib
import subprocess
import sys

from shutil import which


def notify():
  try:
    if sys.platform == 'win32':
      _notify_windows()
    elif sys.platform == 'darwin':
      _notify_macos()
    else:
      _notify_linux()
  except Exception:
    with contextlib.suppress(Exception):
      _beep()


def _notify_windows():
  import ctypes

  ctypes.windll.user32.MessageBeep(0)


def _notify_macos():
  command = 'afplay' if which('afplay') else None
  if command:
    subprocess.run([command, '/System/Library/Sounds/Glass.aiff'], check=False)


def _notify_linux():
  command = 'paplay' if which('paplay') else 'aplay' if which('aplay') else None
  if command:
    subprocess.run(
      [command, '/usr/share/sounds/freedesktop/stereo/complete.oga'],
      check=False,
    )


def _beep():
  command = 'beep' if which('beep') else None
  if command:
    subprocess.run([command], check=False)

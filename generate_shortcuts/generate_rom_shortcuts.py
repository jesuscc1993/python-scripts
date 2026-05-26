import os
import re
import sys
import winsound

from mtlogger import logger
from mtprompt import Prompt
from win32com.client import Dispatch

from _constants import BINARY_BLACKLIST, ROM_EXTS, BINARY_BY_PLATFORM

def main():
  binaries_dir = sys.argv[1] if len(sys.argv) > 1 else Prompt.dir('Enter the path to the directory containing the emulator binaries')
  roms_dir = sys.argv[2] if len(sys.argv) > 2 else Prompt.dir('Enter the path to the directory containing the ROMs')
  out_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.join(roms_dir, 'shortcuts')

  binaries = find_binaries(binaries_dir)
  roms_by_platform = find_roms(roms_dir)

  generate_shortcuts(binaries, roms_by_platform, out_dir)

def find_binaries(binaries_dir):
  binaries = {}
  if not os.path.isdir(binaries_dir):
    logger.warn(f'Binaries directory does not exist: {binaries_dir}')
    return binaries

  for root, _, files in os.walk(binaries_dir):
    for file in files:
      name, ext = os.path.splitext(file)
      if ext.lower() != '.exe':
        continue
      key = name.lower()
      path = os.path.join(root, file)
      if any(blacklisted in key for blacklisted in BINARY_BLACKLIST):
        logger.dim(f'Skipping blacklisted binary: "{path}"')
        continue
      if key in binaries:
        logger.debug(f'Multiple binaries found for {key}, using: "{path}"')
        continue
      binaries[key] = path

  return binaries

def find_roms(roms_dir):
  roms_by_platform = {}
  if not os.path.isdir(roms_dir):
    logger.warn(f'ROMs directory does not exist: {roms_dir}')
    return roms_by_platform

  entries = [e for e in os.listdir(roms_dir) if not e.startswith('.')]

  platform_dirs = []
  for entry in entries:
    platform_path = os.path.join(roms_dir, entry)
    if os.path.isdir(platform_path):
      platform_dirs.append((entry.lower(), platform_path))

  if not platform_dirs:
    platform_dirs.append((os.path.basename(os.path.normpath(roms_dir)).lower(), roms_dir))

  for platform, path in platform_dirs:
    roms = []
    for root, _, files in os.walk(path):
      for f in files:
        if os.path.splitext(f)[1].lower() in ROM_EXTS:
          roms.append(os.path.join(root, f))
    if len(roms):
      roms_by_platform[platform] = roms

  return roms_by_platform

def generate_shortcuts(binaries, roms_by_platform, out_dir):
  for platform, roms in roms_by_platform.items():
    binary = find_binary_for_platform(platform, binaries)
    if not binary:
      logger.warn(f'No binary found for platform: {platform}')
      continue

    platform_out_dir = os.path.join(out_dir, platform)
    os.makedirs(platform_out_dir, exist_ok=True)
    generate_shortcuts_for_platform(binary, roms, platform_out_dir)

def find_binary_for_platform(platform, binaries):
  platform_key = platform.lower()

  binary_names_for_platform = BINARY_BY_PLATFORM.get(platform_key)
  if binary_names_for_platform:
    for binary_name in binary_names_for_platform:
      if binary_name in binaries:
        path = binaries[binary_name]
        logger.debug(f'Found exact match for {platform}: "{path}"')
        return path

      for key, path in binaries.items():
        if binary_name in key:
          logger.debug(f'Found partial match for {platform}: "{path}"')
          return path

  return None

def generate_shortcuts_for_platform(binary, roms, out_dir):
  for rom in roms:
    generate_rom_shortcut(binary, rom, out_dir)

def generate_rom_shortcut(binary, rom, out_dir):
  try:
    rom_name = os.path.splitext(os.path.basename(rom))[0]
    # rom_name = re.sub(r'\[.*?\]', '', rom_name)
    rom_name = rom_name.replace('꞉', '-')
    shortcut_path = os.path.join(out_dir, rom_name + '.lnk')

    if Dispatch is not None:
      shell = Dispatch('WScript.Shell')
      sc = shell.CreateShortCut(shortcut_path)
      sc.Targetpath = binary
      sc.Arguments = f'"{rom}"'
      sc.WorkingDirectory = os.path.dirname(binary)
      sc.IconLocation = binary
      sc.save()
      logger.success(f'Created shortcut for "{shortcut_path}"')

  except Exception as ex:
    logger.error(f'Failed to create shortcut for "{rom}":\n{ex}')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  winsound.MessageBeep()
  Prompt.enter_to_exit()

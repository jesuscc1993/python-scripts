import shutil
import subprocess

from mtlogger import logger
from mtprompt import Prompt

def main():
  clear_cache_for_package_manager("npm", ["cache", "clean", "--force"])
  clear_cache_for_package_manager("yarn", ["cache", "clean"])
  clear_cache_for_package_manager("pip", ["cache", "purge"])

def clear_cache_for_package_manager(cmd, args):
  exe = shutil.which(cmd)
  if exe:
    try:
      formatted_command = f"{cmd} {' '.join(args)}"
      logger.trace(f"Running: {formatted_command}")
      subprocess.run([exe] + args, check=True)
    except subprocess.CalledProcessError as e:
      logger.error(f"Error running {formatted_command}: {e}")
    print()
  else:
    logger.warning(f"{cmd} not found, skipping.")

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandledError(ex)

  Prompt.enter_to_exit()

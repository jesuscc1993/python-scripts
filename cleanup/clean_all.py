import os
import subprocess
import sys

from concurrent.futures import ThreadPoolExecutor, as_completed

from mtlogger import logger
from mtprompt import Prompt
from pathlib import Path

from _common import run_as_admin


def main():
  run_as_admin()

  env = os.environ.copy()
  env[Prompt.PROMPT__MUTE] = '1'
  env[Prompt.PROMPT__NO_ENTER_TO_EXIT] = '1'

  logger.log('Running all cleanup scripts...')

  scripts = [
    script
    for script in Path(__file__).parent.glob('clean_*.py')
    if script.name != Path(__file__).name
  ]

  with ThreadPoolExecutor() as executor:
    processes = {
      executor.submit(
        subprocess.run,
        [sys.executable, str(script)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
      ): script
      for script in scripts
    }

    for process in as_completed(processes):
      script = processes[process]
      result = process.result()
      if result.returncode:
        logger.error(
          f'{script.name} finished with exit code {result.returncode}.'
        )
      else:
        logger.success(f'{script.name} finished.')

  logger.log('Finished running all cleanup scripts.')


if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()

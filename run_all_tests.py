import subprocess
import sys

from pathlib import Path
from mtlogger import logger

test_files = sorted(
  test_file
  for test_dir in Path('.').rglob('_tests')
  if 'build' not in test_dir.parts
  for test_file in test_dir.glob('test_*.py')
)

results = []

for test_file in test_files:
  logger.log(f'\nTesting "{test_file}"...')
  result = subprocess.run(
    [sys.executable, '-m', 'pytest', str(test_file), '-q'],
    check=False,
  )
  results.append(
    (test_file.name, test_file.parent.parent.name, result.returncode == 0)
  )

passed_count = sum(1 for _, _, passed in results if passed)

logger.log(f'\nTEST RESULTS ({passed_count}/{len(results)}):')
for name, parent, passed in results:
  status = 'PASS' if passed else 'FAIL'
  logger_fn = logger.info if passed else logger.error
  logger_fn(f'  {status}: {parent}/{name}')

sys.exit(0 if all(passed for _, _, passed in results) else 1)

import subprocess
import sys

from pathlib import Path
from mtlogger import logger

test_dirs = sorted(
  test_dir
  for test_dir in Path('.').rglob('_tests')
  if 'build' not in test_dir.parts
)
results = []

for test_dir in test_dirs:
  logger.log(f'\nTesting "{test_dir}"...')
  result = subprocess.run([sys.executable, '-m', 'pytest', '.', '-q'], cwd=str(test_dir))
  results.append((test_dir.name, test_dir.parent.name, result.returncode == 0))

passed_count = sum(1 for _, _, p in results if p)

logger.log(f'\nTEST RESULTS ({passed_count}/{len(results)}):')
for name, parent, passed in results:
  status = 'PASS' if passed else 'FAIL'
  logger_fn = logger.info if passed else logger.error
  logger_fn(f'  {status}: {parent}/{name}')

sys.exit(0 if all(p for _, _, p in results) else 1)

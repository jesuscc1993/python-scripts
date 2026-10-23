import subprocess
import sys

from pathlib import Path

for script in Path(__file__).parent.glob('clean_*.py'):
  if script.name != Path(__file__).name:
    subprocess.run([sys.executable, str(script)], check=True)

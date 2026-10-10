import subprocess

from pathlib import Path

repo_root = Path(__file__).parent
subprocess.run(['ruff', 'check', '--fix', str(repo_root)], check=False)

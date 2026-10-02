import os

from mtattr import Attr
from mtlogger import logger
from tqdm import tqdm

from _constants import DIRECTORY_BLACKLIST

def tqdm_dim(
  msg: str,
):
  tqdm.write(logger.format_trace(msg))

def collect_dirs_to_process(
  parent_dir: str,
  depth: int,
):
  parent_depth = parent_dir.rstrip(os.sep).count(os.sep)

  dirs_to_process = []
  for root, dirs, _ in os.walk(parent_dir):
    dirs[:] = [dir_name for dir_name in dirs if not should_skip_dir(os.path.join(root, dir_name))]

    current_depth = root.rstrip(os.sep).count(os.sep) - parent_depth
    if current_depth >= depth:
      dirs.clear()
      continue

    for dir_name in dirs:
      dirs_to_process.append(os.path.join(root, dir_name))

  return dirs_to_process

def should_skip_dir(
  dir_path: str,
):
  if Attr.is_hidden(dir_path):
    return True

  return os.path.basename(dir_path).lower() in DIRECTORY_BLACKLIST

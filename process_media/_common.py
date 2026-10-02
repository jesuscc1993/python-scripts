from mtlogger import logger
from tqdm import tqdm

def tqdm_dim(
  msg: str,
):
  tqdm.write(logger.format_trace(msg))

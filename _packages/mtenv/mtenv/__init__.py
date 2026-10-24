import os

from mtvalidation import to_bool


class Env:
  @staticmethod
  def bool(name: str, default: bool = False):
    val = os.getenv(name)

    if val is None:
      return default

    try:
      return to_bool(val.strip().lower())
    except ValueError:
      return default

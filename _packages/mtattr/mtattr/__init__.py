import os
import stat
import subprocess

from typing import Literal

AttrKey = Literal['h', 's', 'r']

DEFAULT_ATTRS: list[AttrKey] = ['h']

STATS_BY_ATTR: dict[AttrKey, int] = {
  'h': stat.FILE_ATTRIBUTE_HIDDEN,
  's': stat.FILE_ATTRIBUTE_SYSTEM,
  'r': stat.FILE_ATTRIBUTE_READONLY,
}

def _get_stat_for_attr(attr: AttrKey):
  return STATS_BY_ATTR.get(attr, 0)

class Attr:

  # generic

  @staticmethod
  def add(
    path: str,
    attrs: list[AttrKey],
  ):
    if os.path.exists(path):
      subprocess.run(['attrib'] + ['+' + attr for attr in attrs] + [path], check=True)

  @staticmethod
  def remove(
    path: str,
    attrs: list[AttrKey],
  ):
    if os.path.exists(path):
      subprocess.run(['attrib'] + ['-' + attr for attr in attrs] + [path], check=True)

  @staticmethod
  def has(
    path: str,
    attr: AttrKey,
  ):
    return (
      os.path.exists(path) and
      bool(
        os.lstat(path).st_file_attributes &
        _get_stat_for_attr(attr)
      )
    )

  @staticmethod
  def toggle(
    path: str,
    attr: AttrKey,
  ):
    if os.path.exists(path):
      if Attr.has(path, attr):
        Attr.remove(path, [attr])
      else:
        Attr.add(path, [attr])

  # specific

  @staticmethod
  def is_hidden(
    path: str,
  ):
    return Attr.has(path, 'h')

  @staticmethod
  def is_system(
    path: str,
  ):
    return Attr.has(path, 's')

  @staticmethod
  def is_readonly(
    path: str,
  ):
    return Attr.has(path, 'r')

  @staticmethod
  def toggle_hidden(
    path: str,
  ):
    Attr.toggle(path, 'h')

  @staticmethod
  def toggle_system(
    path: str,
  ):
    Attr.toggle(path, 's')

  @staticmethod
  def toggle_readonly(
    path: str,
  ):
    Attr.toggle(path, 'r')

  @staticmethod
  def hide(
    path: str,
    attrs: list[AttrKey] = DEFAULT_ATTRS,
  ):
    Attr.add(path, attrs)

  @staticmethod
  def show(
    path: str,
    attrs: list[AttrKey] = DEFAULT_ATTRS,
  ):
    Attr.remove(path, attrs)

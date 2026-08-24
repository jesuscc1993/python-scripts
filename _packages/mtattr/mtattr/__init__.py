import os
import stat
import subprocess

DEFAULT_ATTRS = ['h']

class Attr:

  @staticmethod
  def add(
    file_path: str,
    attrs: list[str] = DEFAULT_ATTRS,
  ):
    if os.path.exists(file_path):
      subprocess.run(['attrib'] + ['+' + attr for attr in attrs] + [file_path], check=True)

  @staticmethod
  def remove(
    file_path: str,
    attrs: list[str] = DEFAULT_ATTRS,
  ):
    if os.path.exists(file_path):
      subprocess.run(['attrib'] + ['-' + attr for attr in attrs] + [file_path], check=True)

  @staticmethod
  def hide(
    file_path: str,
    attrs: list[str] = DEFAULT_ATTRS,
  ):
    Attr.add(file_path, attrs)

  @staticmethod
  def show(
    file_path: str,
    attrs: list[str] = DEFAULT_ATTRS,
  ):
    Attr.remove(file_path, attrs)

  @staticmethod
  def is_hidden(
    file_path: str,
  ):
    return bool(os.lstat(file_path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

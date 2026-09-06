import json
import os

UTF8 = 'utf-8'

def read_file(
  path: str,
  mode = 'rb',
  encoding: str = None,
):
  if not os.path.exists(path):
    return None

  with open(path, mode, encoding=encoding) as file:
    return file.read()

def write_file(
  path: str,
  content: bytes,
  mode = 'wb',
  encoding: str = None,
):
  os.makedirs(os.path.dirname(path) or '.', exist_ok=True)

  with open(path, mode, encoding=encoding) as file:
    file.write(content)

def read_text_file(
  path: str,
  encoding = UTF8,
):
  return read_file(path, mode='r', encoding=encoding)

def write_text_file(
  path: str,
  content: str,
  encoding = UTF8,
):
  write_file(path, content, mode='w', encoding=encoding)

def read_json_file(
  path: str,
  encoding = UTF8,
):
  content = read_text_file(path, encoding=encoding)
  return json.loads(content) if content is not None else None

def write_json_file(
  path: str,
  content: object,
  encoding = UTF8,
):
  formattedContent = json.dumps(content, indent=2)
  write_text_file(path, formattedContent, encoding=encoding)

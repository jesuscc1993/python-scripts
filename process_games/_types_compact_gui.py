from enum import IntEnum
from typing import TypedDict

class CompType(IntEnum):
  XPRESS4K = 0
  XPRESS8K = 1
  XPRESS16K = 2
  LZX = 3

class CompressionResult(TypedDict):
  AfterBytes: int
  BeforeBytes: int
  CompType: CompType
  TotalResults: int

class DbEntry(TypedDict):
  CompressionResults: list[CompressionResult]
  Confidence: int
  FolderName: str
  GameName: str
  PoorlyCompressedExtensions: dict[str, int]
  SteamID: int
  TotalFiles: int

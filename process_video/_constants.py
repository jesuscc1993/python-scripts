REPLACE_COLOR = True
STRIP_TAGS = True

## BBGGRR
LOOKUP_TEXT_COLOR = 'FFFFFF'
REPLACEMENT_TEXT_COLOR = '55FFFF'

ENCODING = 'utf-8'
HTML_FONT_ATTRIBUTES = ['color', 'face', 'size']

STRIP_SETTINGS = {
  'fonts': True,
  'color': False,
  'face': False,
  'size': False,
}

VIDEO_EXTS = [
  '.mp4',
  '.mkv'
]

ASS_CODEC = 'ass'
MOV_TEXT_CODEC = 'mov_text'
SRT_CODEC = 'srt'
SSA_CODEC = 'ssa'
SUBRIP_CODEC = 'subrip'
WEBVTT_CODEC = 'webvtt'

ASS_EXT = '.ass'
SRT_EXT = '.srt'
SSA_EXT = '.ssa'
VTT_EXT = '.vtt'

SUBTITLE_EXTS_BY_CODEC = {
  ASS_CODEC: ASS_EXT,
  MOV_TEXT_CODEC: SRT_EXT,
  SRT_CODEC: SRT_EXT,
  SSA_CODEC: SSA_EXT,
  SUBRIP_CODEC: SRT_EXT,
  WEBVTT_CODEC: VTT_EXT,
}

SUBTITLE_EXTS = set(SUBTITLE_EXTS_BY_CODEC.values())

SUBTITLE_EXTS_WITH_HTML_TAGS = {
  SRT_EXT,
  VTT_EXT
}

ASS_SUBTITLE_EXTS = {
  ASS_EXT,
  SSA_EXT
}

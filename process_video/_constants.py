REPLACE_COLOR = True
FORCE_TEXT_COLOR = False
FORCE_BORDER_COLOR = True
STRIP_TAGS = True

## BBGGRR
LOOKUP_TEXT_COLOR = 'FFFFFF'
PREFERRED_TEXT_COLOR = '55FFFF'
PREFERRED_BORDER_COLOR = '000000'

HEX_DIGIT_PATTERN = r'[0-9A-Fa-f]'
HEX_COLOUR_VALUE_PATTERN = rf'{HEX_DIGIT_PATTERN}{{6}}$'

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

ASS_STYLE_PRIMARY_COLOUR_FIELD = 'PrimaryColour'
ASS_STYLE_OUTLINE_COLOUR_FIELD = 'OutlineColour'
ASS_STYLE_OUTLINE_FIELD = 'Outline'

ASS_STYLE_FORMAT_LINE_PATTERN = r'Format:\s*([^\r\n]+)'
ASS_STYLE_LINE_PATTERN = r'Style:\s*([^\r\n]+)'

SRT_TIME_PATTERN = r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})'
VTT_TIME_PATTERN = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})'
ASS_TIME_PATTERN = r'(\d+,)(\d+:\d{2}:\d{2}\.\d{2}),(\d+:\d{2}:\d{2}\.\d{2})'

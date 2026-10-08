ENCODING = 'utf-8'
HEX_DIGIT_PATTERN = r'[0-9A-Fa-f]'
HEX_COLOUR_VALUE_PATTERN = rf'{HEX_DIGIT_PATTERN}{{6}}$'

HTML_FONT_ATTRIBUTES = [
  'color',
  'face',
  'size'
]

HTML_SUPPORTED_TAGS = [
  'b',
  'font',
  'i',
  's',
  'u'
]

AVI_EXT = '.avi'
M4V_EXT = '.m4v'
MKV_EXT = '.mkv'
MOV_EXT = '.mov'
MP4_EXT = '.mp4'
WMV_EXT = '.wmv'

MP4_EXTS = { M4V_EXT, MOV_EXT, MP4_EXT }

VIDEO_EXTS_WITH_MUTAGEN_SUPPORT = MP4_EXTS | { WMV_EXT }
VIDEO_EXTS_WITHOUT_MUTAGEN_SUPPORT = { AVI_EXT, MKV_EXT }
VIDEO_EXTS = VIDEO_EXTS_WITH_MUTAGEN_SUPPORT | VIDEO_EXTS_WITHOUT_MUTAGEN_SUPPORT

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

SUBTITLE_EXTS_WITH_HTML_TAGS = { SRT_EXT, VTT_EXT }
ASS_SUBTITLE_EXTS = { ASS_EXT, SSA_EXT }

ASS_STYLE_PRIMARY_COLOUR_FIELD = 'PrimaryColour'
ASS_STYLE_OUTLINE_COLOUR_FIELD = 'OutlineColour'
ASS_STYLE_OUTLINE_FIELD = 'Outline'
ASS_STYLE_FONTNAME_FIELD = 'Fontname'

ASS_STYLE_FORMAT_LINE_PATTERN = r'Format:\s*([^\r\n]+)'
ASS_STYLE_LINE_PATTERN = r'Style:\s*([^\r\n]+)'

SRT_TIME_PATTERN = r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})'
VTT_TIME_PATTERN = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})'
ASS_TIME_PATTERN = r'(\d+,)(\d+:\d{2}:\d{2}\.\d{2}),(\d+:\d{2}:\d{2}\.\d{2})'

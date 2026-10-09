# NOTE: outline thickness and shadow offset are combined into a single setting
# because they depend on the combination of the ScaledBorderAndShadow flag and
# the video resolution.

SETTINGS = {
  'extract_to_folder': False,

  'strip_settings': {
    'enabled': True,

    'color': False,
    'face': False,
    'fonts': True,
    'size': False,
  },

  'replace_background_color': True,
  'replace_border_color': True,
  'replace_font': False,
  'replace_foreground_color': True,

  'force_background_color': False,
  'force_border_color': False,
  'force_font': True,
  'force_foreground_color': False,
  'force_outline_thickness_and_shadow_offset': True,

  'lookup_background_colors': ['000040'],
  'lookup_border_colors': ['000040'],
  'lookup_fonts': [],
  'lookup_foreground_colors': ['FFFFFF'],

  'preferred_background_color': '000000',
  'preferred_border_color': '000000',
  'preferred_font': 'Quicksand SemiBold',
  'preferred_foreground_color': 'FFFF55',
  'preferred_outline_thickness': '5.0',
  'preferred_shadow_offset': '2.5',
}

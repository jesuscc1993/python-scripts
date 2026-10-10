# NOTES:
# * background color applies both to the background and shadow.
# * outline thickness and shadow offset are combined into a single setting
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
  'replace_font': False,
  'replace_foreground_color': True,
  'replace_outline_color': False,
  'force_background_color': True,
  'force_font': True,
  'force_foreground_color': False,
  'force_outline_color': False,
  'force_outline_thickness_and_shadow_offset': True,
  'lookup_background_colors': ['000040FF'],
  'lookup_fonts': [],
  'lookup_foreground_colors': ['FFFFFFFF'],
  'lookup_outline_colors': ['000040FF'],
  'preferred_background_color': '000000FF',
  'preferred_font': 'Quicksand SemiBold',
  'preferred_foreground_color': 'FFFF55FF',
  'preferred_outline_color': '000000FF',
  'preferred_outline_thickness': '4.0',
  'preferred_shadow_offset': '2.0',
}

import numpy

JPEG_EXTENSION = '.jpeg'
JPG_EXTENSION = '.jpg'
PNG_EXTENSION = '.png'
WEBP_EXTENSION = '.webp'

LOSSLESS = 'lossless'

FILE_EXCLUSIONS = ['folder.jpg', 'cover.jpg']
WEBP_DIMENSION_LIMIT = 16383

def is_image_file(filename):
  name = filename.lower()
  return name.endswith((JPG_EXTENSION, JPEG_EXTENSION, PNG_EXTENSION, WEBP_EXTENSION)) and name not in FILE_EXCLUSIONS

def is_image_monochrome(img, sample_step = 24, sat_threshold = 24):
  hsv = img.convert('HSV')
  arr = numpy.array(hsv)
  arr = arr[::sample_step, ::sample_step]
  s = arr[..., 1]
  return numpy.all(s < sat_threshold)

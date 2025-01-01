JPEG_EXTENSION = '.jpeg'
JPG_EXTENSION = '.jpg'
PNG_EXTENSION = '.png'
WEB_EXTENSION = '.webp'

def is_image_file(filename):
  return filename.lower().endswith((JPG_EXTENSION, JPEG_EXTENSION, PNG_EXTENSION, WEB_EXTENSION))

def is_image_uncompressed(filename):
  return filename.lower().endswith((PNG_EXTENSION))
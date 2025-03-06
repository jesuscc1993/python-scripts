JPEG_EXTENSION = '.jpeg'
JPG_EXTENSION = '.jpg'
PNG_EXTENSION = '.png'
WEBP_EXTENSION = '.webp'

FILE_EXCLUSIONS = ['folder.jpg', 'cover.jpg']

def is_image_file(filename):
  name = filename.lower()
  return name.endswith((JPG_EXTENSION, JPEG_EXTENSION, PNG_EXTENSION, WEBP_EXTENSION)) and name not in FILE_EXCLUSIONS

def is_image_uncompressed(filename):
  return filename.lower().endswith((PNG_EXTENSION))
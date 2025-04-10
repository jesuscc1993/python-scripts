import os

from _settings import OUTPUT_FORMAT, OUTPUT_EXTENSION, OUTPUT_QUALITY

def save_image_to_path(image, path):
  try:
    output_path = f"{os.path.splitext(path)[0]}.{OUTPUT_EXTENSION}"
    image.save(output_path, OUTPUT_FORMAT, quality = OUTPUT_QUALITY)
    return output_path
  except Exception as e:
    print(f"Error saving image '{path}': {e}")
    return None
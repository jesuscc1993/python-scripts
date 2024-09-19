from PIL import Image
import os

DEVICE_HEIGHT = 1920
JPEG_FORMAT = 'JPEG'
JPG_EXTENSION = '.jpg'

def main():
  parent_folder = input("Enter the path to the parent folder containing the folders or images: ")
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    process_images(parent_folder)

def process_images(root_dir):
  for root, _, files in os.walk(root_dir):
    print(f'Processing "{root}"')
    for file in files:
      if is_image_file(file):
        image_path = os.path.join(root, file)
        resize_image(image_path)

def resize_image(image_path):
  with Image.open(image_path) as img:
    width, height = img.size

    # discard alpha channel
    if img.mode != 'RGB':
      img = img.convert('RGB')

    if height > DEVICE_HEIGHT:
      # resize images larger than the target device
      new_height = DEVICE_HEIGHT
      new_width = int((new_height / height) * width)
      img = img.resize((new_width, new_height), Image.LANCZOS)
      output_path = os.path.splitext(image_path)[0] + JPG_EXTENSION
      img.save(output_path, JPEG_FORMAT)
    else:
      # convert images smaller than the target device if they are not JPG
      if not image_path.lower().endswith(JPG_EXTENSION):
        output_path = os.path.splitext(image_path)[0] + JPG_EXTENSION
        img.save(output_path, JPEG_FORMAT)

  # delete original files if they are not JPG
  if not image_path.lower().endswith(JPG_EXTENSION):
    os.remove(image_path)

def is_image_file(filename):
  return filename.lower().endswith(('.jpg', '.jpeg', '.png'))

if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
  input("Press Enter to exit...")

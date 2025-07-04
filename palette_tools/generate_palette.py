import colorsys
import math
import os

from PIL import Image, ImageDraw
from collections import Counter

SQUARE_SIZE = 40
MIN_COLS = 4

def main():
  src_path = input('Enter the path to the image you want to generate the palette for:\n').strip(' "\'')
  generate_palette(src_path)

def generate_palette(image_path):
  colors = extract_colors(image_path)
  folder, filename = os.path.split(image_path)
  name, _ = os.path.splitext(filename)
  output_name = f'{name} (palette).png'
  output_path = os.path.join(folder, output_name)
  create_palette_image(colors, output_path)

def extract_colors(image_path):
  img = Image.open(image_path).convert('RGBA')
  pixels = [p for p in img.getdata() if p[3] > 0]
  count = Counter(pixels)
  def sort_key(c):
    r, g, b = [v / 255 for v in c[0][:3]]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h, s, l)
  sorted_colors = sorted(count.items(), key = lambda x: sort_key(x))
  return [c[0] for c in sorted_colors]

def create_palette_image(colors, output_path):
  if len(colors) > 255:
    return print('ERROR: Palette supports a maximum of 256 colors (transparency included)')

  columns = MIN_COLS * math.ceil(math.sqrt(len(colors)) / MIN_COLS)
  rows = (len(colors) + columns - 1) // columns
  width = columns * SQUARE_SIZE
  height = rows * SQUARE_SIZE
  palette_img = Image.new('P', (width, height), color = 0)

  palette = [0, 0, 0]
  for color in colors:
    palette.extend(color[:3])
  palette += [0] * (768 - len(palette))
  palette_img.putpalette(palette)
  palette_img.info['transparency'] = 0

  draw = ImageDraw.Draw(palette_img)
  for i, color in enumerate(colors):
    x = (i % columns) * SQUARE_SIZE
    y = (i // columns) * SQUARE_SIZE
    draw.rectangle([x, y, x + SQUARE_SIZE, y + SQUARE_SIZE], fill=i + 1)

  palette_img.save(output_path, format = 'PNG', save_all = False)
  print(f'Saved "{output_path}".')

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    print(f'An unexpected error occurred: {ex}')
  input('Press Enter to exit...')

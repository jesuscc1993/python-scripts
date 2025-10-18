import os
import sys
import tkinter

from PIL import Image, ImageTk
from mtlogger import logger

if len(sys.argv) > 1:
  image_path = sys.argv[1]
else:
  image_path = 'overlay.webp'

if not os.path.isfile(image_path):
  logger.error(f'File "{image_path}" does not exist')
  sys.exit(1)

root = tkinter.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.wm_attributes('-transparentcolor', 'magenta')

image = Image.open(image_path).convert('RGBA')
photo_image = ImageTk.PhotoImage(image)
width, height = image.size

root.geometry(f'{width}x{height}+0+0')

canvas = tkinter.Canvas(
  root,
  width = width,
  height = height,
  highlightthickness = 0,
  bd = 0,
  bg = 'magenta'
)
canvas.pack()
canvas.create_image(0, 0, anchor = 'nw', image = photo_image)

root.lift()
root.bind('<Escape>', lambda e: root.destroy())
root.mainloop()

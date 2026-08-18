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

def start_root_drag(
  ev,
):
  root.x_offset = ev.x
  root.y_offset = ev.y

def drag_root(
  _,
):
  x = root.winfo_pointerx() - root.x_offset
  y = root.winfo_pointery() - root.y_offset
  root.geometry(f'+{x}+{y}')

def reset_root_position(
  _,
):
  root.geometry(f'{width}x{height}+0+0')

def hide_root(
  _,
):
  root.attributes('-alpha', 0.0)

def show_root(
  _,
):
  root.attributes('-alpha', 1.0)

def destroy_root(
  _,
):
  root.destroy()

root.bind('<KeyPress-Control_L>', hide_root)
root.bind('<KeyRelease-Control_L>', show_root)
root.bind('<Escape>', destroy_root)

canvas.bind('<B1-Motion>', drag_root)
canvas.bind('<Button-1>', start_root_drag)
canvas.bind('<Button-2>', reset_root_position)
canvas.bind('<Button-3>', destroy_root)

root.mainloop()

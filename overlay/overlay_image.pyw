import os
import sys
import tkinter
import ctypes

from PIL import Image, ImageTk
from mtlogger import logger

GWL_EX_STYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020

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

hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EX_STYLE)
ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EX_STYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)

def hide_overlay(e):
  root.attributes('-alpha', 0.0)

def show_overlay(e):
  root.attributes('-alpha', 1.0)

def close_overlay(e):
  root.destroy()

root.bind('<KeyPress-Control_L>', hide_overlay)
root.bind('<KeyRelease-Control_L>', show_overlay)
root.bind('<Escape>', close_overlay)
root.mainloop()

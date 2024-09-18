# iterates and opens a browser tab for each steam game folder
# drop in your Steam saves folder

import os
import webbrowser

for filename in os.scandir("."):
    if filename.is_dir():
        webbrowser.open("https://store.steampowered.com/app/" + filename.name)
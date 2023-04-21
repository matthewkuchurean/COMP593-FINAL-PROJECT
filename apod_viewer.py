from tkinter import *
from tkinter import ttk
import inspect
import os
import apod_desktop
from PIL import Image, ImageTk
from tkcalendar import Calendar, DateEntry


# Determine the path and parent directory of this script
script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
script_dir = os.path.dirname(script_path)


# Initialize the image cache
apod_desktop.init_apod_cache(script_dir)

root = Tk()
root.geometry('600x400')

# Create a basic GUI
root.title("Astronomy Picture of the Day")
root.rowconfigure(0, weight=95)
root.rowconfigure(1, weight=5)
root.columnconfigure(0, weight=50)
root.columnconfigure(1, weight=50)

# Image Frame
image_frame = ttk.LabelFrame(root, text="Image Frame")
image_frame.grid(row=0, column=0, sticky='nsew', columnspan=2, padx=20, pady=20)

root.mainloop()
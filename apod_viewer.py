from tkinter import *
from tkinter import ttk
import inspect
import os
import apod_desktop
from PIL import Image, ImageTk
from tkcalendar import Calendar, DateEntry
import sqlite3
from datetime import date, date

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




frm_top = ttk.Frame(root)
frm_top.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
frm_top.rowconfigure(0, weight=75)
frm_top.columnconfigure(0, weight=75)

frm_btm_left = ttk.LabelFrame(root, text='View Cached Image')
frm_btm_left.grid(row=1, column=0, sticky=NSEW)
frm_btm_left.rowconfigure(0, weight=75)
frm_btm_left.columnconfigure(0, weight=75)

frm_btm_right = ttk.LabelFrame(root, text='Get More Images')
frm_btm_right.grid(row=1, column=1, sticky=NSEW)
frm_btm_right.rowconfigure(0, weight=75)
frm_btm_right.columnconfigure(0, weight=75)

lbl_image = ttk.LabelFrame(frm_btm_left, text='View Cached Image')
lbl_image.grid(row=1, column=0)

lbl_cal = ttk.LabelFrame(frm_btm_right, text='Get More Images')
lbl_cal.grid(row=1, column=1)

path = os.path.join(script_dir, 'logo.png')
logo = Image.open(path)
img_nasa = ImageTk.PhotoImage(logo)
lbl_nasa = ttk.Label(frm_top, image=img_nasa)
lbl_nasa.grid(row=0, column=0)



lbl_explan = ttk.Label(frm_top, text='', wraplength=600, anchor=N)
lbl_explan.grid(row=1, column=0)

lbl_title = ttk.Label(frm_btm_left, text='Select image')
lbl_title.grid(row=1, column=1, padx=10, pady=10, sticky=NSEW)

desktop_names_list = sorted(apod_desktop.get_all_apod_titles())
nasa_names = ttk.Combobox(frm_btm_left, values=desktop_names_list, width=50, state='readonly')
nasa_names.set("Select an image")
nasa_names.grid(row=1, column=2, padx=10, pady=10, sticky=NSEW)

def handle_NASA(event):
    global image_path
    user_pick = nasa_names.get()
    image_db = apod_desktop.image_cache_db
    con = sqlite3.connect(image_db)
    cur = con.cursor()
    title_query = """
    SELECT explanation, path, title FROM image_cache
    WHERE title=?
    """
    cur.execute(title_query, (user_pick,))
    query_result = cur.fetchone()
    con.close()
 
    title = query_result[2]
    image_path = query_result[1]
    explanation = query_result[0]
    
    img = Image.open(image_path)
    # width, height = img.size

    # scale = image_lib.scale_image((width, height))
    scale = (700, 400)
    img.thumbnail(scale, Image.LANCZOS)
    img2 = ImageTk.PhotoImage(img)
    lbl_nasa.configure(image=img2)
    lbl_nasa.image = img2
    lbl_explan.configure(text=explanation)
    lbl_explan.text = explanation
    nasa_names.set(title)


nasa_names.bind('<<ComboboxSelected>>', handle_NASA)


lbl_cal = ttk.Label(frm_btm_right, text='Select Date')
lbl_cal.grid(row=1, column=1, padx=10, pady=10, sticky=NSEW)




today = date.today()
lower = date(1995, 6, 16)
calen = DateEntry(frm_btm_right, maxdate=today, mindate=lower)
calen.grid(row=1, column=2, padx=10, pady=10, sticky=NSEW)


def handle_date_sel():

    global image_path
    date_sel = calen.get_date()
    format_date = date_sel.strftime('%Y-%m-%d')
    info = apod_desktop.add_apod_to_cache(format_date)
    apod_info = apod_desktop.get_apod_info(info)
    title = apod_info['title']
    explanation = apod_info['explanation']
    image_path = apod_info['file_path']
    desktop_names_list.append(title)
    img = Image.open(image_path)
    # width, height = img.size

    # scale = image_lib.scale_image((width, height))
    scale = (800, 600)
    img.thumbnail(scale)
    img2 = ImageTk.PhotoImage(img)
    lbl_nasa.configure(image=img2)
    lbl_nasa.image = img2
    lbl_explan.configure(text=explanation)
    lbl_explan.text = explanation
    nasa_names.set(title)


def image_change():
    global image_path
    image_lib.set_desktop_background_image(image_path)


root.mainloop()
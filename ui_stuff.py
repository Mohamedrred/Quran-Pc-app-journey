import customtkinter as ctk
from PIL import Image

quran_font = 'arial'
font_size = 16

def create_optionmenu(master, values, anchor, command=None):
    option_menu = ctk.CTkOptionMenu(master, values=values, anchor=anchor, font=(quran_font, font_size), dropdown_font=(quran_font, font_size), command=command)
    return option_menu

def create_button(master, anchor, text=None, command=None):
    button = ctk.CTkButton(master, text=text, anchor=anchor, command=command, font=(quran_font, font_size))
    return button

def create_button_with_id_for_imgs(master, image_path, id, command=None):
    image = Image.open(image_path)
    image_width, image_height = image.size  # Get the original image size
    image_ctk = ctk.CTkImage(image, size=(image_width, image_height))  # Set the image size
    button = ctk.CTkButton(master, image=image_ctk, command=command, text='')
    button.id = id
    return button

def create_slider(master, command=None):
    slider = ctk.CTkSlider(master, from_=0, to=1, command=command)
    return slider

def create_checkbox(master, text, checkvar):
    checkbox = ctk.CTkCheckBox(master, text=text, onvalue=True, offvalue=False, command=checkvar)
    return checkbox
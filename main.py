import pystray
import os
import json
import tkinter as tk
from PIL import Image

logo = Image.open(os.path.join("assets", "PulsePause.png"))

disable_var = tk.BooleanVar()
interval_var = tk.IntVar()

def save_settings():
    global disable_var, interval_var
    settings = {
        "disable_app": disable_var.get(),
        "check_in_interval": interval_var.get()
    }
    with open("settings.json", "w") as f:
        json.dump(settings, f)

def load_settings():
    global disable_var, interval_var
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.load(f)
            disable_var.set(settings.get("disable_app", False))
            interval_var.set(settings.get("check_in_interval", 60))
    else:
        # Default settings
        disable_var.set(False)
        interval_var.set(60)
        save_settings()

def open_settings():
    root = tk.Tk()
    root.iconbitmap(os.path.join("assets", "PulsePause.ico"))
    root.title("Settings")

    tk.Checkbutton(root, text="Disable Application", variable=disable_var).pack()
    tk.Label(root, text="Check-in Interval (minutes):").pack()
    tk.Entry(root, textvariable=interval_var).pack()

    tk.Button(root, text="Save", command=save_settings).pack()

    load_settings()
    root.mainloop()

def after_click(icon, query):
    if str(query) == "Check In":
        print("The Best Place to learn anything Tech \
        Related -> https://www.geeksforgeeks.org/")
    elif str(query) == "Settings":
        open_settings()
    elif str(query) == "Exit":
        icon.stop()
        # Save settings before exiting
        save_settings()

icon = pystray.Icon("PP", logo, "PulsePause", 
                    menu=pystray.Menu(
    pystray.MenuItem("Check In", 
                     after_click),
    pystray.MenuItem("Settings", 
                     after_click),
    pystray.MenuItem("Exit", after_click)))
load_settings()
icon.run()
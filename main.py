import pystray
import os
import json
import tkinter as tk
import yarppg
import cv2
from PIL import Image
import time
import threading

logo = Image.open(os.path.join("assets", "PulsePause.png"))

rppg = yarppg.Rppg()

disable_var = tk.BooleanVar()
interval_var = tk.IntVar()

FONT_COLOR = (0, 0, 0)

def _is_window_closed(name: str) -> bool:
    return cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE) < 1

def check_in(skip_permission=False):
    """
    Perform a mindfulness check-in using the webcam to measure heart rate.

    Parameters:
    skip_permission (bool): If True, skip the permission prompt for the check-in. Default is False.

    Returns:
    int: Returns -1 if the camera could not be openedor the user skipped check-in, otherwise 0.
    """
    if not disable_var.get():
        if not skip_permission:
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            if not tk.messagebox.askyesno("Mindfulness Check-In", "Are you ready for a brief mindfulness check-in?"):
                return -1
            root.destroy()

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print(f"Could not open camera")
            return -1
        tracker = yarppg.FpsTracker()
        start_time = time.time()
        # Run for five seconds
        while time.time() - start_time < 5:
            ret, frame = cam.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if not ret:
                break
            result = rppg.process_frame(frame)
            img = yarppg.roi.overlay_mask(
                frame, result.roi.mask != 0, alpha=0.0
            )
            img = cv2.flip(img, 1)
            tracker.tick()
            result.hr = 60 * tracker.fps / result.hr
            text = f"{result.hr:.1f} (bpm)"
            pos = (10, img.shape[0] - 10)
            cv2.putText(img, text, pos, cv2.FONT_HERSHEY_COMPLEX, 0.8, color=FONT_COLOR)
            cv2.imshow("Checking stress level, please wait...", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            print(result.value, result.hr)
            if cv2.waitKey(1) == ord("q") or _is_window_closed("yarPPG"):
                break
        cam.release()
        cv2.destroyAllWindows()
        return 0

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
        check_in(True)
    elif str(query) == "Settings":
        open_settings()
    elif str(query) == "Exit":
        icon.stop()
        # Save settings before exiting
        save_settings()

def schedule_check_in():
    interval = interval_var.get() * 60  # Convert minutes to seconds
    if not disable_var.get():
        check_in()
    threading.Timer(interval, schedule_check_in).start()

icon = pystray.Icon("PP", logo, "PulsePause", 
                    menu=pystray.Menu(
                        pystray.MenuItem("Check In", 
                                         after_click),
                        pystray.MenuItem("Settings", 
                                         after_click),
                        pystray.MenuItem("Exit", after_click))
                    )
load_settings()
schedule_check_in()
icon.run()
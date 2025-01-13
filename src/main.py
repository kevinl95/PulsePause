import pystray
import os
import json
import tkinter as tk
import yarppg
import cv2
import time
import random
import threading
import sys
from PIL import Image
from tkinter import messagebox

logo = Image.open(os.path.join("assets", "PulsePauseIcon.png"))

rppg = yarppg.Rppg()

root = tk.Tk()
root.withdraw()  # Hide the root window

disable_var = tk.BooleanVar(root)
interval_var = tk.IntVar(root)
athlete_var = tk.BooleanVar(root)

FONT_COLOR = (0, 0, 0)

mindfulness_exercises = [
    {
        "name": "Deep Breathing",
        "description": "Take a deep breath in for 4 seconds, hold it for 4 seconds, and then exhale for 6 seconds. Repeat for 5 cycles."
    },
    {
        "name": "Body Scan",
        "description": "Close your eyes and slowly bring attention to different parts of your body, starting from your toes and working up to your head."
    },
    {
        "name": "5-4-3-2-1 Grounding",
        "description": "Identify 5 things you can see, 4 things you can feel, 3 things you can hear, 2 things you can smell, and 1 thing you can taste."
    },
    {
        "name": "Gratitude Reflection",
        "description": "Take 2 minutes to reflect on 3 things you’re grateful for and why they are meaningful to you."
    },
    {
        "name": "Mindful Observation",
        "description": "Choose an object nearby and focus on it for 1 minute. Observe its color, texture, shape, and any small details you’ve never noticed before."
    }
]

def is_heart_rate_anomalous(heart_rate, age_group="adult"):
    """
    Checks if the heart rate is anomalously high for the specified age group.
    
    Parameters:
        heart_rate (float): The measured heart rate in BPM.
        age_group (str): The age group of the user ("child", "adult", "athlete").
    
    Returns:
        bool: True if the heart rate is anomalous, False otherwise.
        str: A message explaining the result.
    """
    thresholds = {
        "adult": 100,
        "athlete": 80
    }
    
    if age_group not in thresholds:
        return False, "Unknown age group. Cannot determine threshold."
    
    threshold = thresholds[age_group]
    
    if heart_rate > threshold:
        return True, f"High heart rate detected! Measured: {heart_rate} BPM (Threshold: {threshold} BPM). It's time for a break."
    else:
        return False, f"Heart rate is normal: {heart_rate} BPM (Threshold: {threshold} BPM)."


def _is_window_closed(name: str) -> bool:
    return cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE) < 1

def check_in(skip_permission=False):


    """
    Perform a mindfulness check-in using the webcam to measure heart rate.

    Parameters:
        skip_permission (bool): If True, skip the permission prompt for the check-in. Default is False.

    Returns:
        int: Returns -1 if the camera could not be opened or the user skipped check-in, otherwise 0.
    """
    if not disable_var.get():
        if not skip_permission:
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            if not messagebox.askyesno("Mindfulness Check-In", "Are you ready for a brief mindfulness check-in?"):
                return -1
            root.destroy()

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print(f"Could not open camera")
            return -1
        tracker = yarppg.FpsTracker()
        start_time = time.time()
        heart_rates = []
        while time.time() - start_time < 1000:
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
            heart_rates.append(result.hr)
            text = f"{result.hr:.1f} (bpm)"
            pos = (10, img.shape[0] - 10)
            cv2.putText(img, text, pos, cv2.FONT_HERSHEY_COMPLEX, 0.8, color=FONT_COLOR)
            cv2.imshow("Checking stress level, please wait...", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            print(result.value, result.hr)
            if cv2.waitKey(1) == ord("q") or _is_window_closed("yarPPG"):
                break
        cam.release()
        cv2.destroyAllWindows()

        if heart_rates:
            avg_heart_rate = sum(heart_rates) / len(heart_rates)
            age_group = "athlete" if athlete_var.get() else "adult"
            is_anomalous, message = is_heart_rate_anomalous(avg_heart_rate, age_group)
            if is_anomalous:
                exercise = random.choice(mindfulness_exercises)
                message += f"\n\nSuggested Exercise: {exercise['name']}\n{exercise['description']}"
                messagebox.showwarning("High Stress Alert", message)
            else:
                messagebox.showinfo("Stress Check-In", "Your heart rate is normal. Keep up the good work!")
        return 0

def save_settings(root=None):
    global disable_var, interval_var, athlete_var
    settings = {
        "disable_app": disable_var.get(),
        "check_in_interval": interval_var.get(),
        "is_athlete": athlete_var.get()
    }
    with open("settings.json", "w") as f:
        json.dump(settings, f)
    if root:
        root.quit()  # Exit the settings window after saving

def load_settings():
    global disable_var, interval_var, athlete_var
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.load(f)
            disable_var.set(settings.get("disable_app", False))
            interval_var.set(settings.get("check_in_interval", 60))
            athlete_var.set(settings.get("is_athlete", False))
    else:
        # Default settings
        disable_var.set(False)
        interval_var.set(60)
        athlete_var.set(False)
        save_settings()

def open_settings():
    root = tk.Tk()
    root.iconbitmap(os.path.join("assets", "PulsePause.ico"))
    root.title("Settings")

    tk.Checkbutton(root, text="Disable Application", variable=disable_var).pack()
    tk.Label(root, text="Check-in Interval (minutes):").pack()
    tk.Entry(root, textvariable=interval_var).pack()
    interval_var.set(interval_var.get())  # Ensure the entry widget is populated with the value
    tk.Checkbutton(root, text="Are you an athlete?", variable=athlete_var).pack()

    # Populate the inputs with the initial values
    disable_var.set(disable_var.get())
    interval_var.set(str(interval_var.get()))
    athlete_var.set(athlete_var.get())

    tk.Button(root, text="Save", command=lambda: save_settings(root)).pack()

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
        sys.exit()

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
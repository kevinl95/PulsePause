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
from tkinter import Toplevel, Label, Button, Entry, Checkbutton

icon_path = os.path.join("assets", "PulsePause.ico")
logo = Image.open(icon_path)

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
        "description": "Take a deep breath in for 4 seconds, hold it for 4 seconds, and then exhale for 6 seconds. Repeat for 5 cycles.",
    },
    {
        "name": "Body Scan",
        "description": "Close your eyes and slowly bring attention to different parts of your body, starting from your toes and working up to your head.",
    },
    {
        "name": "5-4-3-2-1 Grounding",
        "description": "Identify 5 things you can see, 4 things you can feel, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
    },
    {
        "name": "Gratitude Reflection",
        "description": "Take 2 minutes to reflect on 3 things you’re grateful for and why they are meaningful to you.",
    },
    {
        "name": "Mindful Observation",
        "description": "Choose an object nearby and focus on it for 1 minute. Observe its color, texture, shape, and any small details you’ve never noticed before.",
    },
]


def custom_messagebox(title, message):
    """
    Creates a custom message box with a given title and message.

    Args:
        title (str): The title of the message box window.
        message (str): The message to be displayed in the message box.

    The message box will have an "OK" button to close the window.
    The window will be modal, meaning it will block interaction with other windows until it is closed.
    """
    msg_box = Toplevel(root)
    msg_box.title(title)
    msg_box.iconbitmap(icon_path)

    Label(msg_box, text=message).pack(pady=10)
    Button(msg_box, text="OK", command=msg_box.destroy).pack(pady=5)

    msg_box.grab_set()
    root.wait_window(msg_box)


def custom_askyesno(title, message):
    """
    Display a custom Yes/No dialog box with the given title and message.

    Parameters:
    title (str): The title of the dialog box.
    message (str): The message to be displayed in the dialog box.

    Returns:
    bool: True if the user clicks 'Yes', False if the user clicks 'No'.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    result = [False]

    def on_yes():
        result[0] = True
        msg_box.destroy()

    def on_no():
        result[0] = False
        msg_box.destroy()

    msg_box = Toplevel(root)
    msg_box.title(title)
    msg_box.iconbitmap(icon_path)

    Label(msg_box, text=message).pack(pady=10)
    Button(msg_box, text="Yes", command=on_yes).pack(side="left", padx=10, pady=5)
    Button(msg_box, text="No", command=on_no).pack(side="right", padx=10, pady=5)

    msg_box.grab_set()
    root.wait_window(msg_box)
    root.destroy()
    return result[0]


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
    thresholds = {"adult": 100, "athlete": 80}

    if age_group not in thresholds:
        return False, "Unknown age group. Cannot determine threshold."

    threshold = thresholds[age_group]

    if heart_rate > threshold:
        return (
            True,
            f"High heart rate detected! Measured: {heart_rate} BPM (Threshold: {threshold} BPM). It's time for a break.",
        )
    else:
        return (
            False,
            f"Heart rate is normal: {heart_rate} BPM (Threshold: {threshold} BPM).",
        )


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
            if not custom_askyesno(
                "Stress Check-In",
                "Are you ready for a brief mindfulness check-in?",
            ):
                return -1
            root.destroy()

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print(f"Could not open camera")
            return -1
        tracker = yarppg.FpsTracker()
        start_time = time.time()
        heart_rates = []
        while time.time() - start_time < 20:
            ret, frame = cam.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if not ret:
                break
            result = rppg.process_frame(frame)
            img = yarppg.roi.overlay_mask(frame, result.roi.mask != 0, alpha=0.0)
            img = cv2.flip(img, 1)
            tracker.tick()
            result.hr = 60 * tracker.fps / result.hr
            heart_rates.append(result.hr)
            if result.hr > 0:
                text = f"{result.hr:.1f} (bpm)"
            else:
                text = "Analyzing..."
            pos = (10, img.shape[0] - 10)
            (text_width, text_height), _ = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_COMPLEX, 0.8, 1
            )
            background_top_left = (pos[0] - 5, pos[1] - text_height - 5)
            background_bottom_right = (pos[0] + text_width + 5, pos[1] + 5)
            cv2.rectangle(
                img,
                background_top_left,
                background_bottom_right,
                (255, 255, 255),
                cv2.FILLED,
            )
            cv2.putText(img, text, pos, cv2.FONT_HERSHEY_COMPLEX, 0.8, color=FONT_COLOR)
            cv2.imshow(
                "Checking stress level, please wait...",
                cv2.cvtColor(img, cv2.COLOR_RGB2BGR),
            )
            cv2.waitKey(1)
        cam.release()
        cv2.destroyAllWindows()

        if heart_rates:
            avg_heart_rate = sum(heart_rates) / len(heart_rates)
            age_group = "athlete" if athlete_var.get() else "adult"
            is_anomalous, message = is_heart_rate_anomalous(avg_heart_rate, age_group)
            if is_anomalous:
                exercise = random.choice(mindfulness_exercises)
                message += f"\n\nSuggested Exercise: {exercise['name']}\n{exercise['description']}"
                custom_messagebox("High Stress Alert", message)
            else:
                custom_messagebox(
                    "Stress Check-In",
                    "Your heart rate is normal. Keep up the good work!",
                )
        schedule_check_in()  # Schedule the next check-in
        return 0


def save_settings(show_message=True):
    """
    Save the current application settings to a JSON file and schedule a check-in if the interval or disable state has changed.

    This function retrieves the current values of `disable_var`, `interval_var`, and `athlete_var` and saves them
    to a file named "settings.json". If the check-in interval or disable state has changed, it schedules a new check-in. 
    Finally, it displays a message box to inform the user that the settings have been saved.

    Parameters:
        show_message (bool): If True, display a message box to inform the user that the settings have been saved. Default is True.

    Globals:
        disable_var (tk.BooleanVar): A Tkinter variable indicating whether the application is disabled.
        interval_var (tk.IntVar): A Tkinter variable holding the check-in interval in minutes.
        athlete_var (tk.BooleanVar): A Tkinter variable indicating whether the user is an athlete.

    Raises:
        FileNotFoundError: If the "settings.json" file does not exist.
        json.JSONDecodeError: If the "settings.json" file contains invalid JSON.
    """
    global disable_var, interval_var, athlete_var
    old_disable = None
    old_interval = None
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.load(f)
            old_disable = settings.get("disable_app", False)
            old_interval = settings.get("check_in_interval", 60)
    new_disable = disable_var.get()
    new_interval = interval_var.get()
    settings = {
        "disable_app": new_disable,
        "check_in_interval": new_interval,
        "is_athlete": athlete_var.get(),
    }
    with open("settings.json", "w") as f:
        json.dump(settings, f)
    if old_interval != new_interval or old_disable != new_disable:
        schedule_check_in()
    if show_message:
        custom_messagebox("PulsePause", "Your settings have been saved.")


def load_settings():
    """
    Load application settings from a JSON file and set global variables accordingly.

    This function checks if a "settings.json" file exists in the current directory.
    If the file exists, it reads the settings from the file and updates the global
    variables `disable_var`, `interval_var`, and `athlete_var` with the values from
    the file. If the file does not exist, it sets the global variables to default
    values and calls `save_settings()` to create the file with these default values.

    Global Variables:
        disable_var (tk.BooleanVar): Indicates whether the application is disabled.
        interval_var (tk.IntVar): The interval for checking in, in minutes.
        athlete_var (tk.BooleanVar): Indicates whether the user is an athlete.

    Raises:
        FileNotFoundError: If the "settings.json" file does not exist and cannot be created.
        json.JSONDecodeError: If the "settings.json" file contains invalid JSON.
    """
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
        save_settings(False)


def open_settings():
    """
    Opens the settings window for the application.

    This function creates a new Toplevel window that allows the user to modify
    application settings such as disabling the application, setting the check-in
    interval, and indicating if the user is an athlete. The settings window includes
    checkboxes and entry fields for these settings, and a save button to save the changes.
    If the user is an athlete, the threshold for being stressed is lower than for non-athletes.

    Global Variables:
    - disable_var: Tkinter variable associated with the "Disable Application" checkbox.
    - interval_var: Tkinter variable associated with the "Check-in Interval" entry field.
    - athlete_var: Tkinter variable associated with the "Are you an athlete?" checkbox.

    The function also sets the window icon, title, and size, and ensures that the settings
    window is modal, meaning it must be closed before the user can interact with the main
    application window again.
    """
    global disable_var, interval_var, athlete_var
    settings_window = Toplevel(root)
    settings_window.iconbitmap(os.path.join("assets", "PulsePause.ico"))
    settings_window.title("Settings")
    settings_window.geometry("300x200")  # Set the size of the settings window
    load_settings()

    checkbox = Checkbutton(
        settings_window, text="Disable Application", variable=disable_var
    )
    checkbox.pack(pady=10)

    Label(settings_window, text="Check-in Interval (minutes):").pack(pady=5)
    interval_entry = Entry(settings_window, textvariable=interval_var)
    interval_entry.pack(pady=5)

    athlete_box = Checkbutton(
        settings_window, text="Are you an athlete?", variable=athlete_var
    )
    athlete_box.pack(pady=10)

    save_button = Button(settings_window, text="Save", command=save_settings)
    save_button.pack(pady=10)

    settings_window.grab_set()
    root.wait_window(settings_window)


def after_click(icon, query):
    """
    Handles actions based on the user's selection from a menu.

    Parameters:
    icon (Icon): The icon object representing the system tray icon.
    query (str): The user's selection from the menu.

    Actions:
    - If the query is "Check In", it calls the check_in function with True as an argument.
    - If the query is "Settings", it calls the open_settings function.
    - If the query is "Exit", it stops the icon, destroys all OpenCV windows, and exits the program.
    """
    if str(query) == "Check In":
        check_in(True)
    elif str(query) == "Settings":
        open_settings()
    elif str(query) == "Exit":
        icon.stop()
        cv2.destroyAllWindows()
        sys.exit()


def schedule_check_in():
    """
    Schedules a periodic check-in based on the interval set by the user.

    This function retrieves the interval from `interval_var`, converts it from minutes to seconds,
    and schedules the `check_in` function to be called after the specified interval.
    Note:
        This function uses threading to schedule the check-ins.

    Variables:
        interval_var (tkinter.Variable): A Tkinter variable holding the interval in minutes.
        disable_var (tkinter.Variable): A Tkinter variable indicating whether the check-in is disabled.

    Returns:
        None
    """
    if not disable_var.get():
        interval = interval_var.get() * 60  # Convert minutes to seconds
        threading.Timer(interval, check_in).start()


icon = pystray.Icon(
    "PP",
    logo,
    "PulsePause",
    menu=pystray.Menu(
        pystray.MenuItem("Check In", after_click),
        pystray.MenuItem("Settings", after_click),
        pystray.MenuItem("Exit", after_click),
    ),
)
load_settings()
schedule_check_in()
icon.run()

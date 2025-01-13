from cx_Freeze import setup, Executable
import os
import sys

# Include the assets directory
assets_dir = os.path.join("assets")

# Define the executable
executables = [
    Executable(
        script="src/main.py",
        base="Win32GUI" if sys.platform == "win32" else None,
        icon=os.path.join(assets_dir, "PulsePause.ico"),
        target_name="PulsePause.exe"
    )
]

# Setup configuration
setup(
    name="PulsePause",
    version="1.0",
    description="A mindfulness check-in application using computer vision to measure heart rate.",
    options={
        "build_exe": {
            "packages": ["pystray", "cv2", "numpy", "scipy", "matplotlib", "PIL", "tkinter"],
            "include_files": [assets_dir],
            "include_msvcr": True
        }
    },
    executables=executables
)
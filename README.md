# PulsePause - Mindfulness Check-in From your System Tray
![A heart made out of a fast fourier transform is displayed above the text Pulse Pause - Mindfulness App.](assets/PulsePause.png)

[![Build EXE](https://github.com/kevinl95/PulsePause/actions/workflows/build.yml/badge.svg)](https://github.com/kevinl95/PulsePause/actions/workflows/build.yml)

PulsePause is a Python-based desktop application designed to help users practice mindfulness by periodically measuring heart rate using computer vision and providing alerts when stress levels appear elevated. It accomplishes this using [remote photoplethysmography (rPPG)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9267568/). Once an hour (or however often the user chooses!) users will be prompted for a check-in. The web cam will be opened and a five second video captured. Using rPPG the users heart rate is collected and if the user is stressed they are prompted to take a break and are given one of a set of mindfulness exercises to practice.

---

![Someone is looking at the camera while overlayed in black text on top of the video output is the text 58.1 bpm](screenshots/stresslevel.PNG)

## Features
- Measure heart rate using computer vision and your webcam.
- Identify anomalously high heart rates as a potential indicator of stress.
- Provide mindfulness exercises to promote relaxation.
- Unobtrusively runs from the system tray

![A menu with the options Check In, Settings, and Exit are overlayed over an icon with a heart and the text "PP" in a Windows system tray](screenshots/tray.png)

## Settings

![A menu with the options Disable Application, Check-in Interval (Minutes), and "Are you an Athlete" is shown in a window](screenshots/settings.PNG)

Settings can be accessed by clicking the Pulse Pause icon in the system tray.

- Disable Application lets you disable check-ins. This is good if you wish to be disturbed for a while.
- Check-in Interval lets you choose how often PulsePause prompts you for a check in. You can always click "No" when asked if you do not have time for a check-in. Check-ins can be triggered manually from the system tray whenver you wish
- "Are you an Athlete?" lowers the stress threshold level since your heart rate will be lower.

---

## Prerequisites
Ensure you have the following installed:

1. **Python 3.12**
   - [Download Python 3.12](https://www.python.org/downloads/release/python-3127/)
   
2. **Poetry**
   - Poetry is a dependency management and packaging tool for Python.
   - Install Poetry using the following command:
     ```bash
     curl -sSL https://install.python-poetry.org | python3 -
     ```
   - After installation, ensure Poetry is added to your PATH:
     ```bash
     export PATH="$HOME/.local/bin:$PATH"
     ```

---

## Installation Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/kevinl95/PulsePause.git
   cd PulsePause
   ```

2. Install project dependencies using Poetry:
   ```bash
   poetry install
   ```
   This command will set up a virtual environment and install all required dependencies listed in the `pyproject.toml` file.

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

---

## Running the Application

1. Launch the application:
   ```bash
   poetry run python src/main.py
   ```
   The application will start, and you can begin using PulsePause.

---

## Downloading Executables

For your convenience, pre-built executables for Windows are available on the [GitHub Releases page](https://github.com/kevinl95/PulsePause/releases). These executables require no additional installation steps.

Unpack the PulsePause archive and run PulsePause.exe.

### Note for First-Time Users

On the first run, it is normal for PulsePause to take several moments to set itself up before launching. Please be patient as it completes its initialization process.

## Building Executables
PulsePause uses `cx_Freeze` to build standalone executables for distribution.

### Steps to Build Executables:

1. Ensure you are in the project directory.

2. Run the `setup.py` script with the following command:
   ```bash
   python setup.py build
   ```

3. The built executable will be located in the `build/exe.<platform>` directory.
   - Example (Windows): `build/exe.win32-3.12/PulsePause.exe`

## Contributing
We welcome contributions! Please fork the repository, create a new branch for your feature or bugfix, and submit a pull request.

---
## Disclaimer

PulsePause is not a medical device. The heart rate information provided by this application is approximate and intended for general wellness purposes only. It is not designed to diagnose, treat, cure, or prevent any medical condition. If you have health concerns or require accurate heart rate measurements, please consult a qualified healthcare professional.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Thank you for using PulsePause! Stay mindful and stress-free.


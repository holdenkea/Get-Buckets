## Table of Contents
- [About](#about)
- [Getting Started](#getting-started)
  - [Setting up MaUWB_DW3000 Modules](#module-setup)   
- [Running](#running-the-program)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## About
Shooting machine 

## Getting Started

### Module Setup
  1) Install Arduino IDE
      - V1.8.10/V1.8.19
  2) Go to Tools-> Board -> Boards Manager -> Search and Install ESP32 Board Package 
      - Project is based on the ESP32-S3 development board by Espressif Systems
      - Version 3.2.0-RC1 at time of writing
  3) Go to Tools -> Manage Libraries -> Search and Install Adafruit SSD1306 Library
      - Version 2.5.13 at time of writing
      - If "The library Adafruit SSD1306:version neeeds some other library dependecies..."
     message shows up, Install all missising dependencies.




Clone Repository

Set up virtual environment from terminal

python -m venv "yourvenvname"

## Dependencies
Activate venv
.\venv\Scripts\Activate

or

/"yourvenvname"/Scripts/Activate

Once in venv
pip install mediapipe opencv-python

Deactivating venv
deactivate

IF "ImportError: DLL load failed while importing _framework_bindings: A dynamic link library (DLL) initialization routine failed." for cv2, mediapipe, and numpy, try to change python interpreter version, 

Install a python version between 3.7 and 3.10, for me I used 3.10.2

Then, check versions using py -0

Now run py -3.10 -m venv venv

Activate venv and try to run

## Running the Program
python main.py

## License
Apache License 2.0 

## Acknowledgements
Mention youtuber 

Nicholas Renotte

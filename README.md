## Table of Contents
- [About](#about)
- [Getting Started](#getting-started)
  - [Setting up MaUWB_DW3000 Modules](#arduino-ide-setup)   
- [Running](#running-the-program)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## About
Welcome to my Get Buckets repository! This project was driven by my love for the game of basketball, and how I would have to fill out "shot charts" for my basketball teams as a young kid 

This project combines a real-time pose classifier, UWB modules for indoor positioning, and a simple UI to track, save, and visualize where on the court shots were made and missed.

For a full tutorial of my data collection and model building process you can visit my [colab notebook.](https://colab.research.google.com/drive/1WI-09Oz9cyWwPGClQgsOGs4Z_GwHAM_2?usp=sharing).

## Getting Started

### Arduino IDE Setup
  1) Install Arduino IDE
      - V1.8.10/V1.8.19
  2) Go to Tools-> Board -> Boards Manager -> Search and Install ESP32 Board Package 
      - Project is based on the ESP32-S3 development board by Espressif Systems
      - Version 3.2.0-RC1 at time of writing
  3) Go to Tools -> Manage Libraries -> Search and Install Adafruit SSD1306 Library
      - Version 2.5.13 at time of writing
      - If "The library Adafruit SSD1306:version neeeds some other library dependecies..."
     message shows up, Install all missising dependencies.
  4) Set Board using Tools -> Board -> ESP32 Arduino -> ESP32S3 Dev Module
  5) Plug in USB Type-C into module and machine running Arduino IDE
      - Select Tools -> Port -> (Serial Port for your connection)
      -     
### Setting Up Tag Module  
This project uses one tag.
  1) Navigate to src -> uwb -> tags -> ... and open in Arduino IDE
  2) Verify code using the Verify Button or Sketch -> Verify/Compile (Ctrl+R)
  3) Upload code using the Upload Button or Sketch -> Upload (Ctrl+U)

### Setting Up Anchor Modules
This project uses three anchors.
  1) Navigate to src -> uwb -> anchors -> ...
  2) Verify and Upload Code.

### Arduino IDE Serial Monitor
Once all code is uploaded, check distance and signal strengths of tag to anchors.
  1) Navigate to Tools -> Serial Monitor
  2)                                                                    

[Manufacturer Instructions](https://wiki.makerfabs.com/MaUWB_ESP32S3%20UWB%20module.html)

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

IF ImportError: DLL load failed while importing _pywrap_tensorflow_internal: A dynamic link library (DLL) initialization routine failed.       


Failed to load the native TensorFlow runtime.
See https://www.tensorflow.org/install/errors for some common causes and solutions.
If you need help, create an issue at https://github.com/tensorflow/tensorflow/issues and include the entire stack trace above this error message.

Uninstall tensorflow

Try pip install tensorflow==2.10

NEW REDO 
python -m venv venv312 ( I am using python version 3.12.4 )
activate venv

versions to match colab version I used for training
pip install tensorflow==2.18.0 mediapipe==0.10.13 opencv-python

pip install PyQt5 pyqtgraph pyserial

## Running the Program
python main.py

## License
Apache License 2.0 

## Acknowledgements
Links to revisit:

- [Module Used](https://www.makerfabs.com/mauwb-esp32s3-uwb-module.html)
- [Makerfabs Github for Modules](https://github.com/Makerfabs/MaUWB_ESP32S3-with-STM32-AT-Command)
- [Makerfabs Wiki](https://wiki.makerfabs.com/MaUWB_ESP32S3%20UWB%20module.html)
- [UWB Positioning w/ Python](https://wiki.makerfabs.com/UWB%20positioning%20development%20with%20python.html)


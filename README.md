## Table of Contents
- [About](#about)
- [Featured Images](#featured images)
- [Demo](#demo-video)
- [Getting Started](#getting-started)
  - [Set up Virtual Environment](#set-up-virtual-environment)  
  - [Clone the Repo](#clone-the-repo)
  - [Running the Program](#running-the-program)
  - [Setting up UWB Modules](#setting-up-uwb-modules)
  - [Setting up Arduino Nano](#setting-up-arduino-nano)
  - [Break Beam Sensor and Basketball Chute](#break-beam-sensor-and-basketball-chute)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## About
Welcome to my Get Buckets repository! This project was driven by my love for the game of basketball, and how I would have to fill out "shot charts" for my basketball teams as a young kid.

This project combines a real-time pose classifier, UWB modules for indoor positioning, and a simple UI to track, save, and visualize where on the court shots were made and missed.

For a full tutorial of my data collection and model building process you can visit my [colab notebook](https://colab.research.google.com/drive/1WI-09Oz9cyWwPGClQgsOGs4Z_GwHAM_2?usp=sharing).

<img width="716" alt="image" src="https://github.com/user-attachments/assets/7dca0c20-c75a-4396-9df0-0253694f9381" />

## Demo Video

## Getting Started

### Setting up Virtual Environment
```
# initialize virtual environment
python -m venv venv312 # (I am using python version 3.12.4)

# activate venv
.\venv312\Scripts\Activate

# download dependencies using pip
pip install tensorflow==2.18.0 mediapipe==0.10.13 opencv-python

pip install PyQt5 pyqtgraph pyserial
```

If you encounter any of the following errors, it is most likely due to a version mismatch, try to use the exact versions I specified.

  1) IF "ImportError: DLL load failed while importing _framework_bindings: A dynamic link library (DLL) initialization routine failed." for cv2, mediapipe, and numpy, try to change python interpreter version, 

  2) IF ImportError: DLL load failed while importing _pywrap_tensorflow_internal: A dynamic link library (DLL) initialization routine failed.       

### Clone the Repo
```
# clone the repo
git clone <repository url>
```

### Running the Program
```
python src/gui/main.py
```

### Setting up UWB Modules
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
        
### Setting Up Tag Module  
This project uses one tag.
  1) Navigate to src -> uwb -> esp32...t0 -> ... and open in Arduino IDE
  2) Make sure the UWB index is set to 0 and that the #define is "TAG"
  3) Verify code using the Verify Button or Sketch -> Verify/Compile (Ctrl+R)
  4) Upload code using the Upload Button or Sketch -> Upload (Ctrl+U)

### Setting Up Anchor Modules
This project uses three anchors.
  1) Navigate to src -> uwb -> esp32...a0 -> ... and open in Arduino IDE
  2) Make sure to increment the UWB index every time you upload the code to a new anchor.
  3) Verify and Upload Code.

### Arduino IDE Serial Monitor
Once all code is uploaded, you can check distances and signal strengths of anchors to the tag.
  1) Navigate to Tools -> Serial Monitor
  2) The anchors will send distances to the tag in the form of AT+RANGE commands in the form of range:(d0,d1,d2,...)                                                                 
For more comprehensive instructions you can view the [manufacturer instructions.](https://wiki.makerfabs.com/MaUWB_ESP32S3%20UWB%20module.html)

### Setting up Arduino Nano
  1) Open a new Sketch in the Arduino IDE
  2) Use the same ESP32 Board Package by Espressif Systems
  3) Select the "Arduino Nano ESP32" Board
  4) Specify a Baud rate of 9600
  5) Plug in usb to machine
  6) Navigate to src -> beam -> esp32nano -> esp32nano.ino
  7) Replace ssid and password with your credentials
  8) Verify and Upload Code
  9) Use Arduino ide Serial Monitor to see and copy the IP address for the ESP32 module
  10) Use the found IP address as input in the GUI

### Break Beam Sensor and Basketball Chute
  1) Break beam sensor has transmitter and reciever sides
  2) Reciever side wired to Arduino Nano Pin 5 and Ground
  3) Power drawn from 5v battery pack
  4) Beam breaks communicated over wifi through Arduino Nano ESP32



## License
Apache License 2.0 

## Acknowledgements
Product Links:

- [UWB Module](https://www.makerfabs.com/mauwb-esp32s3-uwb-module.html)
- [Makerfabs Github for Modules](https://github.com/Makerfabs/MaUWB_ESP32S3-with-STM32-AT-Command)
- [Makerfabs Wiki](https://wiki.makerfabs.com/MaUWB_ESP32S3%20UWB%20module.html)

- [Arduino Nano ESP32](https://www.amazon.com/dp/B0C947C9QS?ref=ppx_yo2ov_dt_b_fed_asin_title)
- [Break Beam Sensor](https://www.amazon.com/dp/B09V76Z4CB?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)
- [Portable Battery Packs](https://www.amazon.com/dp/B094Y1R46V?ref=ppx_yo2ov_dt_b_fed_asin_title)
- [Basketball Chute](https://www.amazon.com/dp/B0D6W4CCYZ?ref=ppx_yo2ov_dt_b_fed_asin_title)


## Table of Contents
- [About](#about)
- [Getting Started](#getting-started)
- [Running](#running-the-program)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## About
Shooting machine 

## Getting Started
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

## Acknowledgements
Mention youtuber 

Nicholas Renotte

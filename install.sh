#!/bin/bash

# this install script was tested with python 3.11.2

sudo apt update 
sudo apt upgrade -y

sudo apt remove python3-rpi.gpio

sudo apt install -y git python3-pip python3-venv python3-rpi-lgpio i2c-tools sqlite3 mpg321 libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg python3-pyaudio flac python3-espeak espeak
sudo apt install -y python3-picamera2 --no-install-recommends

python3 -m venv --system-site-packages .venv 
python3 -m pip install pyaudio
source .venv/bin/activate

pip3 install -r requirements.txt
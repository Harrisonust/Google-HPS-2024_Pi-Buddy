#!/bin/bash

# this install script was tested with python 3.11.2

sudo apt update 
sudo apt upgrade -y

sudo apt remove python3-rpi.gpio

sudo apt install -y python3-rpi-lgpio
sudo apt install -y git python3-pip python3-venv python3-rpi-lgpio i2c-tools 
sudo apt install -y python3-picamera2 --no-install-recommends

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt


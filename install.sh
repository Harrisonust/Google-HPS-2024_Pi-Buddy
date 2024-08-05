#!/bin/bash

sudo apt update 
sudo apt upgrade -y

sudo apt install -y git python3-pip python3-venv i2c-tools libopenjp2-7

python3 -m venv .venv
source .venv/bin/activate

pip install rpi.gpio smbus spidev pillow


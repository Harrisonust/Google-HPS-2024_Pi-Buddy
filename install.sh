#!/bin/bash

sudo apt update 
sudo apt upgrade -y

sudo apt install -y git python3-pip python3-venv i2c-tools

python3 -m venv .venv
source .venv/bin/activate

pip install rpi.gpio smbus spidev adafruit-blinka adafruit-circuitpython-ssd1306 adafruit-circuitpython-framebuf


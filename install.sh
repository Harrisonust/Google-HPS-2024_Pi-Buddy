#!/bin/bash

sudo apt update 
sudo apt upgrade -y

sudo apt install -y git python3-pip python3-venv i2c-tools

python3 -m venv .venv
source .venv/bin/activate

pip install rpi.gpio smbus spidev pyaudio pillow

# respeaker
git clone https://github.com/respeaker/seeed-voicecard ~/seeed-voicecard/
cd ~/seeed-voicecard
sudo ./install.sh
sudo reboot
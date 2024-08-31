#!/bin/bash

# this install script was tested with python 3.11.2

sudo apt update 
sudo apt upgrade -y

sudo apt remove python3-rpi.gpio

<<<<<<< Updated upstream
sudo apt install -y git python3-pip python3-venv python3-rpi-lgpio i2c-tools sqlite3 mpg321 libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg
=======
sudo apt install -y git python3-pip python3-venv python3-rpi-lgpio i2c-tools sqlite3 mpg321 libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg python3-pyaudio flac python3-espeak espeak

>>>>>>> Stashed changes
sudo apt install -y python3-picamera2 --no-install-recommends

python3 -m venv --system-site-packages .venv 
source .venv/bin/activate

pip3 install -r requirements.txt

source ./respeaker_install.sh 

# mic hat with audio examples
git clone git@github.com:respeaker/mic_hat.git ~/mic_hat

sudo echo "defaults.pcm.rate_converter "samplerate"

pcm.!default {
    type asym
    playback.pcm "playback"
    capture.pcm "capture"
}

pcm.playback {
    type plug
    slave.pcm "dmixed"
}

pcm.capture {
    type plug
    slave.pcm "mono_capture"
}

pcm.dmixed {
    type dmix
    slave.pcm "hw:seeed2micvoicec"
    ipc_key 555555
}

pcm.mono_capture {
    type route
    slave {
        pcm "hw:seeed2micvoicec"
        channels 1
    }
    ttable.0.0 1
    ttable.1.0 0
}" > /etc/asound.conf


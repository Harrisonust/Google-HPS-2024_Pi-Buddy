import time
from pin_defines import *
from components.encoder import Encoder

def encoder_task():
    encoder = Encoder(PIN_MENU_ENC1A, PIN_MENU_ENC1B)
    while 1:
        print(encoder.get_position())
        time.sleep(1)

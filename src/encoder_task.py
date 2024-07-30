import time
from components.encoder import Encoder

def encoder_task():
    encoder = Encoder(9, 10)
    while 1:
        print(encoder.get_count())
        time.sleep(1)

import threading
import time
import RPi.GPIO as GPIO
from components.led import LED
from components.button import Button
from components.encoder import Encoder

def blink_task():
    led = LED(22)
    while 1:
        led.blocking_blink(1)

def button_task():
    button = Button(27)
    #while 1:
    #    if button.pressed():
    #        print("pressed")
    #    time.sleep(1)
    button.add_callback(lambda pin: print("hello"), bouncetime=100)

def encoder_task():
    encoder = Encoder(9, 10)
    while 1:
        print(encoder.get_count())
        time.sleep(1)

# the starting point of the program
def main():
    GPIO.setmode(GPIO.BCM)
    led_task_handle = threading.Thread(target=blink_task)
    button_task_handle = threading.Thread(target=button_task)
    encoder_task_handle = threading.Thread(target=encoder_task)
    
    led_task_handle.start()
    button_task_handle.start()
    encoder_task_handle.start()
    
    led_task_handle.join()
    button_task_handle.join()
    encoder_task_handle.join()

if __name__ == '__main__':
    main()

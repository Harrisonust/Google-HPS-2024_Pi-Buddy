import threading
import RPi.GPIO as GPIO
from led_task import blink_task
from button_task import button_task
from encoder_task import encoder_task

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

    GPIO.cleanup()

if __name__ == '__main__':
    main()

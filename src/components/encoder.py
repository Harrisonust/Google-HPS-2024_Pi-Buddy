import time
import RPi.GPIO as GPIO

class Encoder:
    def __init__(self, pin_a, pin_b):
        self.__pin_a = pin_a
        self.__pin_b = pin_b
        self.__cnt = 0
        
        GPIO.setup((self.__pin_a, self.__pin_b), GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.__pin_a, GPIO.FALLING, callback=self.__enc_callback)
        
    def __enc_callback(self, pin):
        state = GPIO.input(self.__pin_b)
        if(state == GPIO.HIGH):
            self.__cnt += 1
        else:
            self.__cnt -= 1
            
    def get_count(self):
        return self.__cnt

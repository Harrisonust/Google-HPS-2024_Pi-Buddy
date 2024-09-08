import time
import RPi.GPIO as GPIO
import multiprocessing
import threading

class Encoder:
    def __init__(self, pin_a, pin_b):
        self.__pin_a = pin_a
        self.__pin_b = pin_b
        self.__position = 0
        
        GPIO.setup((self.__pin_a, self.__pin_b), GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.__pin_a, GPIO.FALLING, callback=self.__enc_callback, bouncetime=1)
        
    def __enc_callback(self, pin):
        state = GPIO.input(self.__pin_b)
        if(state == GPIO.HIGH):
            self.__position += 1
        else:
            self.__position -= 1
    
    # return current position
    # 轉一個刻度數字會變化 1
    # 要加上 capacitor 不然會有 bouncing effect, 會過於敏感
    def get_position(self):
        return self.__position

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    encoder1 = Encoder(0, 5)
    encoder2 = Encoder(6, 13)
    
    while 1:
        print(encoder1.get_position(), encoder2.get_position())
        time.sleep(1)

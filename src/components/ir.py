import RPi.GPIO as GPIO
import time

class IR:
    def __init__(self, pin):
        self.__pin = pin
        self.__current_state = GPIO.HIGH # IR default state is high

        GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
        GPIO.add_event_detect(self.__pin, GPIO.BOTH, callback=self.__ir_callback, bouncetime=200)

    # triggers if distance is less than a pre-defined threshold
    def is_triggered(self) -> bool: 
        return self.__current_state == GPIO.HIGH

    # returns 0 or 1; does pretty much the same thing as is_triggered
    def get_state(self) -> int:
        return self.__current_state

    def __ir_callback(self, pin) -> None:
        if GPIO.input(self.__pin) == GPIO.HIGH:
            self.__current_state = GPIO.HIGH
        else:
            self.__current_state = GPIO.LOW

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    ir = IR(26)
    while 1:
        print(ir.get_state())
        time.sleep(0.1)

import RPi.GPIO as GPIO

class Button:
    def __init__(self, pin, pull_up_down=GPIO.PUD_DOWN):
        self.__pin = pin
        self.__state = None
        self.__pud = pull_up_down
        
        GPIO.setup(self.__pin, GPIO.IN, pull_up_down=self.__pud)

    def pressed(self):
        if self.__pud == GPIO.PUD_DOWN:
            return self.read() == GPIO.HIGH
        elif self.__pud == GPIO.PUD_UP:
            return self.read() == GPIO.LOW
        else:
            print("state undefined")
            return False

    def read(self):
        self.__state = GPIO.input(self.__pin)
        return self.__state
    
    def add_callback(self, callback, bouncetime=200):
        edge = None
        if self.__pud == GPIO.PUD_DOWN:
            edge = GPIO.RISING
        elif self.__pud == GPIO.PUD_UP:
            edge = GPIO.FALLING
        else:
            edge = None

        GPIO.add_event_detect(self.__pin, edge, callback=callback, bouncetime=bouncetime)

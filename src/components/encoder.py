import time
import RPi.GPIO as GPIO

class Encoder:
    def __init__(self, pin_a, pin_b, pull_up=True):
        self._pin_a = pin_a
        self._pin_b = pin_b
        self._position = 0
        self._last_position = 0
        self._last_update_time = 0
        if pull_up == True:
            GPIO.setup((self._pin_a, self._pin_b), GPIO.IN, pull_up_down=GPIO.PUD_UP)
        else:
            GPIO.setup((self._pin_a, self._pin_b), GPIO.IN)
        
        GPIO.add_event_detect(self._pin_a, GPIO.FALLING, callback=self.__enc_callback)
        
    def __enc_callback(self, pin):
        state = GPIO.input(self._pin_b)
        if(state == GPIO.HIGH):
            self._position += 1
        else:
            self._position -= 1
            
    def get_position(self) -> int:
        return self._position

    def get_speed(self) -> float:
        current_time = time.time()
        current_position = self.get_position()
        delta_time = current_time - self._last_update_time 

        speed = (current_position - self._last_position)/delta_time

        self._last_position = current_position
        self._last_update_time = current_time
        return speed


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    encoder = Encoder(0, 5)
    while 1:
        print(encoder.get_position())
        time.sleep(1)

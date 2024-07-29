import RPi.GPIO as GPIO
import time

class LED:
    def __init__(self, pin, continuous_mode=False):
        self.__pin = pin
        self.__duty_cycle = 100
        self.__state = GPIO.LOW
        self.__last_blink = 0
        self.__pwm = None
        self.__continuous_mode = continuous_mode

        GPIO.setup(self.__pin, GPIO.OUT, initial=self.__state)
        if self.__continuous_mode:
            self.__pwm = GPIO.PWM(self.__pin, 100)
            self.__pwm.start(self.__duty_cycle)

    def on(self):
        if self.__continuous_mode:
            print("error, to use LED.on(), please set let continuous mode to False")
            return False
        self.__state = GPIO.HIGH
        GPIO.output(self.__pin, self.__state)

    def off(self):
        if self.__continuous_mode:
            print("error, to use LED.off(), please set let continuous mode to False")
            return False
        self.__state = GPIO.HIGH
        GPIO.output(self.__pin, self.__state)

    def off(self):
        self.__state = GPIO.LOW
        GPIO.output(self.__pin, self.__state)

    def adjust_intensity(self, intensity):
        if not self.__continuous_mode:
            print("error, to set intensity, please set let continuous mode to True")
            return False
        self.__duty_cycle = intensity
        self.__pwm.ChangeDutyCycle(self.__duty_cycle)

    def blocking_blink(self, interval):
        flag = self.on()
        if flag == False:
            return False
        time.sleep(interval/2)
        
        flag = self.off()
        if flag == False:
            return False
        time.sleep(interval/2)
        return True

    def nonblocking_blink(self, interval):  
        if time.time() - self.__last_blink >= interval/2:
            if self.__state == GPIO.LOW:
                flag = self.on()
                if flag == False: 
                    return False
            if self.__state == GPIO.HIGH:
                flag = self.off()
                if flag == False:
                    return False
            self.__last_blink = time.time()
        return True

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    led = LED(22)
    for _ in range(10):
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)

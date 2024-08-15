import RPi.GPIO as GPIO
import time
from enum import Enum

class Rotation(Enum):
    CLOCKWISE = 0
    COUNTER_CLOCKWISE = 1

class SingleChannelMotor:
    def __init__(self, pin_pwm, pin_in1, pin_in2):
        self._pin_pwm  = pin_pwm
        self._pin_in1  = pin_in1
        self._pin_in2  = pin_in2

        self._pwm = None
        self._rotation = Rotation.CLOCKWISE
        self._duty_cycle = 0

        GPIO.setup(self._pin_pwm, GPIO.OUT)
        self._pwm = GPIO.PWM(self._pin_pwm, 1000)
        self._pwm.start(self._duty_cycle)
        
        GPIO.setup(self._pin_in1, GPIO.OUT)
        GPIO.setup(self._pin_in2, GPIO.OUT)

        self.set_rotation(self._rotation)

    def set_rotation(self, rotation=Rotation.CLOCKWISE) -> None:
        self._rotation = rotation
        if self._rotation == Rotation.CLOCKWISE:
            GPIO.output(self._pin_in1, GPIO.HIGH)
            GPIO.output(self._pin_in2, GPIO.LOW)
        if self._rotation == Rotation.COUNTER_CLOCKWISE:
            GPIO.output(self._pin_in1, GPIO.LOW)
            GPIO.output(self._pin_in2, GPIO.HIGH)

    def get_rotation(self) -> int:
        return self._rotation

    def set_duty(self, duty_cycle: float) -> None:
        assert duty_cycle <= 100.0 and duty_cycle >= 0.0, "duty_cycle should range from 0.0 ~ 100.0"
        self._duty_cycle = duty_cycle
        self._pwm.ChangeDutyCycle(self._duty_cycle)

    def get_duty(self) -> float:
        return self._duty_cycle

    def brake(self) -> None:
        GPIO.output(self._pin_in1, GPIO.HIGH)
        GPIO.output(self._pin_in2, GPIO.HIGH)
        self.set_duty(0.0)

    def get_speed(self) -> float:
        pass

    def set_speed(self, speed) -> None:
        pass

class DualChannelMotor: 
    def __init__(self, pin_pwm_a, pin_ina1, pin_ina2, pin_pwm_b, pin_inb1, pin_inb2, pin_standby=None):
        self._pin_pwm_a   = pin_pwm_a
        self._pin_ina1    = pin_ina1
        self._pin_ina2    = pin_ina2
        self._pin_pwm_b   = pin_pwm_b
        self._pin_inb1    = pin_inb1
        self._pin_inb2    = pin_inb2
        self._pin_standby = pin_standby
        
        self.left_motor  = SingleChannelMotor(self._pin_pwm_a, self._pin_ina1, self._pin_ina2)
        self.right_motor = SingleChannelMotor(self._pin_pwm_b, self._pin_inb1, self._pin_inb2)
        if self._pin_standby is not None:
            GPIO.setup(self._pin_standby, GPIO.OUT)
            self.enable()
        
    # to be tested    
    def enable(self) -> None: 
        assert self._pin_standby is not None, "to use motor.enable(), please assign a pin to pin standby"
        GPIO.output(self._pin_standby, GPIO.HIGH)
    
    # to be tested
    def disable(self) -> None:
        assert self._pin_standby is not None, "to use motor.enable(), please assign a pin to pin standby"
        GPIO.output(self._pin_standby, GPIO.LOW)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    motor_driver = DualChannelMotor(23, 24, 25, 1, 12, 16, pin_standby=None)
    for duty in range(50, 110, 10):
        if duty % 20 == 10:
            motor_driver.left_motor.set_rotation(Rotation.CLOCKWISE)
            motor_driver.right_motor.set_rotation(Rotation.CLOCKWISE)
        else:
            motor_driver.left_motor.set_rotation(Rotation.COUNTER_CLOCKWISE)
            motor_driver.right_motor.set_rotation(Rotation.COUNTER_CLOCKWISE)
        print(f'rotation: {motor_driver.left_motor.get_rotation()} duty {duty}')
        motor_driver.left_motor.set_duty(duty)
        motor_driver.right_motor.set_duty(duty)
        time.sleep(2)


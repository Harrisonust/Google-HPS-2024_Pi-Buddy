import RPi.GPIO as GPIO
import time
from enum import Enum
import random

class Rotation(Enum):
    CLOCKWISE = 0
    COUNTER_CLOCKWISE = 1

class SingleChannelMotor:
    def __init__(self, pin_pwm, pin_in1, pin_in2, pin_enc1=None, pin_enc2=None):
        self._pin_pwm  = pin_pwm
        self._pin_in1  = pin_in1
        self._pin_in2  = pin_in2
        self._pin_enc1 = pin_enc1
        self._pin_enc2 = pin_enc2

        self._pwm = None
        self._rotation = Rotation.CLOCKWISE
        self._duty_cycle = 0
        self._has_encoder = False

        GPIO.setup(self._pin_pwm, GPIO.OUT)
        self._pwm = GPIO.PWM(self._pin_pwm, 1000)
        self._pwm.start(self._duty_cycle)
        
        GPIO.setup(self._pin_in1, GPIO.OUT)
        GPIO.setup(self._pin_in2, GPIO.OUT)

        if self._pin_enc1 != None and self._pin_enc2 != None:
            self._has_encoder = True
            self._encoder = Encoder(self._pin_enc1, self._pin_enc2, pull_up=False)
            
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
        if self._has_encoder == False: 
            raise ValueError("encoder is not enable for this motor")
            return
        #print(self._encoder.get_position())
        return self._encoder.get_speed()

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
        
        self.move_constant = 0.01
        self.rotate_constant = 0.01
        
    # to be tested    
    def enable(self) -> None: 
        assert self._pin_standby is not None, "to use motor.enable(), please assign a pin to pin standby"
        GPIO.output(self._pin_standby, GPIO.HIGH)
    
    # to be tested
    def disable(self) -> None:
        assert self._pin_standby is not None, "to use motor.enable(), please assign a pin to pin standby"
        GPIO.output(self._pin_standby, GPIO.LOW)

    def move(self, distance):
        if distance == 0:
            return

        self.left_motor.set_duty(10)
        self.right_motor.set_duty(10)
        if distance > 0:
            self.left_motor.set_rotation(Rotation.CLOCKWISE)
            self.right_motor.set_rotation(Rotation.CLOCKWISE)
        elif distance < 0:
            self.left_motor.set_rotation(Rotation.COUNTER_CLOCKWISE)
            self.right_motor.set_rotation(Rotation.COUNTER_CLOCKWISE)
        time.sleep(abs(distance * self.move_constant))
        self.stop()
        
    def rotate(self, angle: float):
        if angle == 0:
            return

        self.left_motor.set_duty(10)
        self.right_motor.set_duty(10)
        if angle > 0:
            self.left_motor.set_rotation(Rotation.CLOCKWISE)
            self.right_motor.set_rotation(Rotation.COUNTER_CLOCKWISE)
        elif angle < 0:
            self.left_motor.set_rotation(Rotation.COUNTER_CLOCKWISE)
            self.right_motor.set_rotation(Rotation.CLOCKWISE)
        time.sleep(abs(angle * self.rotate_constant))
        self.stop()
        
    def stop(self):
        self.left_motor.brake()
        self.right_motor.brake()

    def random_walk(self):
        selection = random.randint(1, 5)
        distance = random.randint(1, 10)
        angle = random.randint(30, 120)
        if selection == 1:
            self.move(distance)
        elif selection == 2:
            self.move(-1 * distance)
        elif selection == 3:
            self.rotate(angle)
        elif selection == 4:
            self.rotate(-1 * angle)
        elif selection == 5: # do nothing
            self.stop()
        time.sleep(3)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    robot_base = DualChannelMotor(23, 24, 25, 1, 12, 16, pin_standby=None)
    robot_base.left_motor.set_rotation(Rotation.CLOCKWISE)
    robot_base.right_motor.set_rotation(Rotation.CLOCKWISE)
    duty = 20 
    robot_base.left_motor.set_duty(duty)
    robot_base.right_motor.set_duty(duty)
    test_start_time = time.time()
    while 1:    
        if time.time() - test_start_time < 10:
            print(f'Motor Test\nrotation: {robot_base.left_motor.get_rotation()} duty {duty}')
            time.sleep(1)
        elif 10 <= time.time() - test_start_time < 15:
            robot_base.move(10)
        elif 15 <= time.time() - test_start_time < 20:
            robot_base.move(-10)
        elif 20 <= time.time() - test_start_time < 25:
            robot_base.rotate(90)
        elif 25 <= time.time() - test_start_time < 30:
            robot_base.rotate(-90)
        elif 30 <= time.time() - test_start_time < 60:
            robot_base.random_walk()

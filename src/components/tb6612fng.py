import RPi.GPIO as GPIO
import time
from enum import Enum
from encoder import Encoder

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
    def __init__(self, pin_pwm_a, pin_ina1, pin_ina2, pin_pwm_b, pin_inb1, pin_inb2, pin_enc1_a=None, pin_enc1_b=None, pin_enc2_a=None, pin_enc2_b=None, pin_standby=None):
        self._pin_pwm_a   = pin_pwm_a
        self._pin_ina1    = pin_ina1
        self._pin_ina2    = pin_ina2
        self._pin_pwm_b   = pin_pwm_b
        self._pin_inb1    = pin_inb1
        self._pin_inb2    = pin_inb2
        self._pin_standby = pin_standby
        self._pin_enc1_a  = pin_enc1_a
        self._pin_enc1_b  = pin_enc1_b
        self._pin_enc2_a  = pin_enc2_a
        self._pin_enc2_b  = pin_enc2_b
        
        self.left_motor  = SingleChannelMotor(self._pin_pwm_a, self._pin_ina1, self._pin_ina2, pin_enc1_a, pin_enc1_b)
        self.right_motor = SingleChannelMotor(self._pin_pwm_b, self._pin_inb1, self._pin_inb2, pin_enc2_a, pin_enc2_b)
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
    start = time.time()
    GPIO.setmode(GPIO.BCM)
    motor_driver = DualChannelMotor(23, 24, 25, 1, 12, 16, pin_enc2_a=4, pin_enc2_b=17, pin_standby=None)
    motor_driver.right_motor.set_rotation(Rotation.COUNTER_CLOCKWISE)
    cnt = 0
    while 1:
        print(f"{cnt} {time.time()-start:.2f},{motor_driver.right_motor._encoder.get_position()},{motor_driver.right_motor.get_speed():.2f}")
        time.sleep(0.3)
        cnt+=1

        if cnt > 100: cnt = 100
        motor_driver.right_motor.set_duty(cnt)
    '''
    for duty in range(50, 110, 10):
        motor_driver.left_motor.get_speed()
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
    '''

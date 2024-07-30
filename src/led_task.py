from components.led import LED

def blink_task():
    led = LED(22)
    while 1:
        led.blocking_blink(0.15)

from .apa102 import APA102
import time
import threading

PIXELS_N = 3
rgb = APA102(num_led=PIXELS_N)
rgb.set_pixel(0, 25, 0, 0)
rgb.set_pixel(1, 0, 25, 0)
rgb.set_pixel(2, 0, 0, 25)
rgb.show()

time.sleep(3)
rgb.clear_strip()

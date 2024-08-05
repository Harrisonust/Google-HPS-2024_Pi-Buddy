import time
from enum import Enum
import RPi.GPIO as GPIO
import spidev
from st7735s_reg import *

class Screen:
    def __init__(self, spi_bus=0, spi_device=0, pin_dc=24, pin_rst=25, pin_cs=None, speed_hz=4000000):
        self._spi = spidev.SpiDev()
        self._spi.open(spi_bus, spi_device)
        self._spi.max_speed_hz = speed_hz

        self._pin_dc  = pin_dc # data/command toggle pin
        self._pin_rst = pin_rst
        self._pin_cs  = pin_cs

        self._background_color = 0x0000

        GPIO.setup(self._pin_dc, GPIO.OUT)
        GPIO.setup(self._pin_rst, GPIO.OUT)
        if self._pin_cs is not None:
            GPIO.setup(self._pin_cs, GPIO.OUT)

        self.reset()
        self.init_display()
        

    def reset(self):
        GPIO.output(self._pin_rst, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self._pin_rst, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self._pin_rst, GPIO.HIGH)
        time.sleep(0.1)

    def write_command(self, cmd):
        GPIO.output(self._pin_dc, GPIO.LOW)
        if self._pin_cs is not None:
            GPIO.output(self._pin_cs, GPIO.LOW)
        self._spi.writebytes([cmd])
        if self._pin_cs is not None:
            GPIO.output(self._pin_cs, GPIO.HIGH)

    def write_data(self, data):
        GPIO.output(self._pin_dc, GPIO.HIGH)
        if self._pin_cs is not None:
            GPIO.output(self._pin_cs, GPIO.LOW)
        self._spi.writebytes(data)
        if self._pin_cs is not None:
            GPIO.output(self._pin_cs, GPIO.HIGH)

    def set_sw_reset(self):
        self.write_command(SWRESET)

    def set_sleep_control(self, in_out):
        if in_out == 0:   # sleep in
            self.write_command(SLPIN)
        elif in_out == 1: # sleep out
            self.write_command(SLPOUT)
        else: 
            raise ValueError('sleep in = 0, sleep out = 1')

    def set_color_mode(self, color_mode) -> None:
        self.write_command(COLMOD)
        if color_mode == 0:   # 12 bit
            self.write_data([0x03])
        elif color_mode == 1: # 16 bit
            self.write_data([0x05])
        elif color_mode == 2: # 18 bit
            self.write_data([0x07])
        else:
            raise ValueError('partial display mode = 0, normal display mode = 1')

    def set_display_on_off(self, on_off: int) -> None:
        if on_off == 0: # off
            self.write_command(DISPOFF)
        elif on_off == 1: # on
            self.write_command(DISPON)
        else:
            raise ValueError("off = 0, on = 1")

    def set_display_mode(self, mode: int) -> None:
        if mode == 0:   # partial display mode
            self.write_command(PTLON)
        elif mode == 1: # normal display mode
            self.write_command(NORON)
        else:
            raise ValueError('partial display mode = 0, normal display mode = 1')


    def set_address(self, row_col: int, from_addr: int, to_addr: int) -> None:
        if row_col == 0:   # row
            self.write_command(RASET)
        elif row_col == 1: # col
            self.write_command(CASET)
        else:
            raise ValueError('row = 0, col = 1')
        
        self.write_data([from_addr >> 8, from_addr & 0xFF, to_addr >> 8, to_addr & 0xFF])

    def set_window(self, x0, y0, x1, y1):
        self.set_address(1, x0, x1)
        self.set_address(0, y0, y1)

    def set_inversion(self, on_off):
        if on_off == 0:   # inversion off
            self.write_command(INVOFF)
        elif on_off == 1: # inversion on
            self.write_command(INVON)
        else:
            raise ValueError('off = 0, on = 1')

    def init_display(self) -> None:
        self.set_sw_reset()  # Software reset
        time.sleep(0.15)

        self.set_sleep_control(1)  # Exit sleep mode
        time.sleep(0.5)
        
        self.set_color_mode(1)
        
        self.write_command(MADCTL)  # Memory access control
        self.write_data([0xC8])
        
        self.set_address(1, 0, 127) # column address from 0 to 127
        self.set_address(0, 0, 127) # row address from 0 to 127
        
        self.set_inversion(0)
        
        self.set_display_mode(1)  # Normal display mode
        
        self.set_display_on_off(1)
        time.sleep(0.1)
    
    def draw_pixel(self, x, y, color) -> None:
        self.set_window(x, y, x, y)
        self.write_command(RAMWR)
        self.write_data([color >> 8, color & 0xFF])

    def draw_vertical_line(self, x, y0, y1, color) -> None:
        self.set_window(x, y0, x, y1)
        self.write_command(RAMWR)
        self.write_data([color >> 8, color & 0xFF])

    def draw_horizontal_line(self, y, x0, x1, color) -> None:
        self.set_window(x0, y, x1, y)
        self.write_command(RAMWR)
        self.write_data([color >> 8, color & 0xFF] * (x1 - x0)) 

    def draw_rectangle(self, x0, y0, x1, y1, color) -> None:
        self.set_window(x0, y0, x1, y1)
        self.write_command(RAMWR)
        for _ in range(y1 - y0):
            self.write_data([color >> 8, color & 0xFF] * (x1 - x0))

    def draw_circle(self, x, y, radius, color):
        buf = [[0x00 for x in range(2*(2*radius+1))] for y in range(2*radius+1)]
        self.set_window(x-radius, y-radius, x+radius, y+radius)
        self.write_command(RAMWR)
        for j in range(2*radius+1):
            for i in range(2*radius+1):
                if((j-radius)**2 + (i-radius)**2 <= radius**2):
                    buf[j][i*2]   = color >> 8
                    buf[j][i*2+1] = color & 0xFF
            self.write_data(buf[j])

    def draw_image(self, path):
        pass

    def fill_screen(self, color) -> None:
        self.draw_rectangle(0, 0, 127, 127, color)

    def clear(self) -> None:
        self.fill_screen(0x0000)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    screen = Screen()
    while 1:
        screen.fill_screen(0xF800)  # Fill screen with red
        time.sleep(0.5)
        screen.fill_screen(0x07E0)  # Fill screen with green
        time.sleep(0.5)
        screen.fill_screen(0x001F)  # Fill screen with blue
        time.sleep(0.5)
        screen.draw_horizontal_line(60, 10, 100, 0xF800)
        time.sleep(0.5)
        screen.draw_rectangle(10, 10, 70, 70, 0x07E0)
        time.sleep(0.5)
        screen.draw_circle(60, 60, 31, 0xF800)
        time.sleep(0.5)
        screen.clear()
        time.sleep(1)

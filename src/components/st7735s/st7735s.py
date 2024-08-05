import time
import math
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import spidev
import RPi.GPIO as GPIO
from st7735s_reg import *

class RGB565Color:
    # https://rgbcolorpicker.com/565
    BLACK   = 0x0000
    WHITE   = 0xFFFF
    BLUE    = 0x001F
    RED     = 0xF800
    GREEN   = 0x07E0
    ORANGE  = 0xFB00
    YELLOW  = 0xFFC0
    PINK    = 0xF814
    CYAN    = 0x07FD
    VIOLET  = 0xC01F

class Screen:
    def __init__(self, spi_bus=0, spi_device=0, pin_dc=24, pin_rst=25, pin_cs=None, speed_hz=4000000, col_dim=128, row_dim=128):
        self._spi = spidev.SpiDev()
        self._spi.open(spi_bus, spi_device)
        self._spi.max_speed_hz = speed_hz

        self._pin_dc  = pin_dc # data/command toggle pin
        self._pin_rst = pin_rst
        self._pin_cs  = pin_cs

        self._col_dim = col_dim
        self._row_dim = row_dim

        self._brush_color      = RGB565Color.WHITE
        self._background_color = RGB565Color.BLACK
        self._chunksize        = 1024

        GPIO.setup(self._pin_dc, GPIO.OUT)
        GPIO.setup(self._pin_rst, GPIO.OUT)
        if self._pin_cs is not None:
            GPIO.setup(self._pin_cs, GPIO.OUT)

        self._reset()
        self._init_display()
        
    def _reset(self):
        GPIO.output(self._pin_rst, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self._pin_rst, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self._pin_rst, GPIO.HIGH)
        time.sleep(0.1)

    def _init_display(self) -> None:
        self.set_sw_reset()  # Software reset
        time.sleep(0.15)

        self.set_sleep_control(1)  # Exit sleep mode
        time.sleep(0.5)
        
        self.set_color_mode(1)
        
        self._write_command(MADCTL)  # Memory access control
        self._write_data([0xC8])
        
        self.set_inversion(0)
        
        self.set_display_mode(1)  # Normal display mode
        
        self.set_display_on_off(1)
        time.sleep(0.1)

    def _write_command(self, cmd):
        GPIO.output(self._pin_dc, GPIO.LOW)
        if self._pin_cs is not None:
            GPIO.output(self._pin_cs, GPIO.LOW)
        self._spi.writebytes([cmd])
        if self._pin_cs is not None:
            GPIO.output(self._pin_cs, GPIO.HIGH)

    def _write_data(self, data):
        GPIO.output(self._pin_dc, GPIO.HIGH)
        if self._pin_cs is not None:
            GPIO.output(self._pin_cs, GPIO.LOW)
        self._spi.writebytes(data)
        if self._pin_cs is not None:
            GPIO.output(self._pin_cs, GPIO.HIGH)
    
    def _set_address(self, row_col: int, from_addr: int, to_addr: int) -> None:
        if row_col == 0:   # row
            self._write_command(RASET)
        elif row_col == 1: # col
            self._write_command(CASET)
        else:
            raise ValueError('row = 0, col = 1')
        
        self._write_data([from_addr >> 8, from_addr & 0xFF, to_addr >> 8, to_addr & 0xFF])

    def _set_area(self, x0, y0, x1, y1):
        self._set_address(1, x0, x1)
        self._set_address(0, y0, y1)
        self._write_command(RAMWR)

    def get_col_dim(self) -> int:
        return self._col_dim
    
    def get_row_dim(self) -> int:
        return self._row_dim
    
    def set_sw_reset(self):
        self._write_command(SWRESET)

    def set_sleep_control(self, in_out):
        if in_out == 0:   # sleep in
            self._write_command(SLPIN)
        elif in_out == 1: # sleep out
            self._write_command(SLPOUT)
        else: 
            raise ValueError('sleep in = 0, sleep out = 1')

    def set_color_mode(self, color_mode) -> None:
        self._write_command(COLMOD)
        if color_mode == 0:   # 12 bit
            self._write_data([0x03])
        elif color_mode == 1: # 16 bit
            self._write_data([0x05])
        elif color_mode == 2: # 18 bit
            self._write_data([0x07])
        else:
            raise ValueError('partial display mode = 0, normal display mode = 1')

    def set_display_on_off(self, on_off: int) -> None:
        if on_off == 0: # off
            self._write_command(DISPOFF)
        elif on_off == 1: # on
            self._write_command(DISPON)
        else:
            raise ValueError("off = 0, on = 1")

    def set_display_mode(self, mode: int) -> None:
        if mode == 0:   # partial display mode
            self._write_command(PTLON)
        elif mode == 1: # normal display mode
            self._write_command(NORON)
        else:
            raise ValueError('partial display mode = 0, normal display mode = 1')

    def set_inversion(self, on_off):
        if on_off == 0:   # inversion off
            self._write_command(INVOFF)
        elif on_off == 1: # inversion on
            self._write_command(INVON)
        else:
            raise ValueError('off = 0, on = 1')

    def set_brush_color(self, color) -> None:
        self._brush_color = color

    def set_background_color(self, color) -> None:
        self._background_color = color
    
    def draw_pixel(self, x, y, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim:
            raise ValueError("pixel out of bound")

        if color is None:
            color = self._brush_color
        self._set_area(x, y, x, y)
        self._write_data([color >> 8, color & 0xFF])

    def draw_vertical_line(self, x, y, len_, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim:
            raise ValueError("pixel out of bound")
        if len_ < 1:
            raise ValueError("len must be greater than 1")

        if color is None:
            color = self._brush_color
        self._set_area(x, y, x, y+len_-1)
        self._write_data([color >> 8, color & 0xFF] * len_)

    def draw_horizontal_line(self, x, y, len_, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim:
            raise ValueError("pixel out of bound")
        if len_ < 1:
            raise ValueError("len must be greater than 1")

        if color is None:
            color = self._brush_color
        self._set_area(x, y, x+len_-1, y)
        self._write_data([color >> 8, color & 0xFF] * len_) 

    def draw_rectangle(self, x, y, xlen, ylen, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim:
            raise ValueError("pixel out of bound")
        if xlen < 1 or ylen < 1:
            raise ValueError("lens must be greater than 1")

        if color is None:
            color = self._brush_color
        self._set_area(x, y, x+xlen-1, y+ylen-1)
        for _ in range(ylen):
            self._write_data([color >> 8, color & 0xFF] * xlen)

    def draw_circle(self, x, y, radius, color=None)->None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim:
            raise ValueError("pixel out of bound")
        if color is None:
            color = self._brush_color
        
        buf = [[self._background_color >> 8, self._background_color & 0xFF] * (2*radius) for _ in range(2*radius)]
        
        self._set_area(x-radius+1, y-radius+1, x+radius, y+radius)
        
        for j in range(-radius, radius):
            for i in range(-radius, radius):
                if i**2 + j**2 < radius**2:
                    buf[j+radius][(i+radius)*2] = color >> 8
                    buf[j+radius][(i+radius)*2+1] = color & 0xFF
            self._write_data(buf[j+radius])

    def draw_sector(self, x, y, radius, start_angle, end_angle, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim:
            raise ValueError("pixel out of bound")
        if color is None:
            color = self._brush_color
        
        start_angle = start_angle % 360
        end_angle   = end_angle % 360

        buf = [[self._background_color >> 8, self._background_color & 0xFF] * (2 * radius) for _ in range(2 * radius)]

        self._set_area(x - radius + 1, y - radius + 1, x + radius, y + radius)

        for j in range(-radius, radius):
            for i in range(-radius, radius):
                if i**2 + j**2 < radius**2:
                    angle = math.degrees(math.atan2(-j, i))
                    angle = angle + 360 if angle < 0 else angle  # Normalize angle to [0, 360)
                    if start_angle <= end_angle:
                        if start_angle <= angle <= end_angle:
                            buf[j + radius][(i + radius) * 2] = color >> 8
                            buf[j + radius][(i + radius) * 2 + 1] = color & 0xFF
                    else:  # Crossing the 0-degree line
                        if angle >= start_angle or angle <= end_angle:
                            buf[j + radius][(i + radius) * 2] = color >> 8
                            buf[j + radius][(i + radius) * 2 + 1] = color & 0xFF
            
            self._write_data(buf[j + radius])

    def draw_text(self, x, y, text, size, color=None) -> None:
        if color is None:
            color = self._brush_color

        font = ImageFont.truetype("./arial.ttf", size)
        image = Image.new("RGB", (self._col_dim, self._row_dim), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((x, y), text, font=font, fill=0xFFFFFF)

        image = image.convert("RGB")
        pixels = list(image.getdata())
        buf = []
        for pixel in pixels:
            r, g, b = pixel
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            buf.append(rgb565 >> 8)
            buf.append(rgb565 & 0xFF)

        self._set_area(x, y, x+len(text)*size-1, y+size-1)
        for i in range(0, len(buf), self._chunksize):
            self._write_data(buf[i:i+self._chunksize])

    def draw_image(self, x, y, width, height, path) -> None:
        if x < 0 or x >= self._col_dim or y < 0 or y >= self._row_dim:
            raise ValueError("Pixel out of bound")
        if (x + width > self._col_dim) or (y + height > self._row_dim):
            raise ValueError("Image exceeds display bounds")

        img = Image.open(path)
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        img = img.convert("RGB")

        pixels = list(img.getdata())
        buf = []
        for pixel in pixels:
            r, g, b = pixel
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            buf.append(rgb565 >> 8)
            buf.append(rgb565 & 0xFF)
        
        self._set_area(x, y, x+width-1, y+height-1)
        for i in range(0, len(buf), self._chunksize):
            self._write_data(buf[i:i+self._chunksize])

    def fill_screen(self, color) -> None:
        if color is None:
            color = self._background_color
        self.draw_rectangle(0, 0, self._col_dim, self._row_dim, color)

    def clear(self) -> None:
        self.fill_screen(0x0000)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    screen = Screen(col_dim=132, row_dim=132)
    screen.clear()

    while 1:
        screen.draw_pixel(0, 0)
        screen.draw_pixel(0, screen.get_row_dim()-1)
        screen.draw_pixel(screen.get_col_dim()-1, 0)
        screen.draw_pixel(screen.get_col_dim()-1, screen.get_row_dim()-1)

        screen.draw_vertical_line(15, 15, 10)
        screen.draw_horizontal_line(30, 10, 20)
        screen.draw_circle(100, 20, 10, RGB565Color.YELLOW)
        screen.draw_image(35, 35, 60, 60, "./google.jpg")
        screen.draw_text(40, 100, "Hello", 14, RGB565Color.WHITE)

        colorlist = [RGB565Color.BLACK, RGB565Color.WHITE, RGB565Color.BLUE, RGB565Color.RED, 
                     RGB565Color.GREEN, RGB565Color.ORANGE, RGB565Color.YELLOW, RGB565Color.PINK, 
                     RGB565Color.CYAN, RGB565Color.VIOLET]
        for index, color in enumerate(colorlist):
            screen.draw_rectangle(10+index*10, 124, 10, 8, color)

    
        time.sleep(1)
        screen.clear()
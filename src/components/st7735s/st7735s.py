import time
import math
from enum import Enum
from PIL import Image, ImageDraw, ImageFont
import spidev
import RPi.GPIO as GPIO
from st7735s_reg import *
import numpy as np
import os
import cv2

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
    def __init__(self, spi_bus=0, spi_device=0, pin_dc=24, pin_rst=25, pin_cs=None, speed_hz=20000000, col_dim=128, row_dim=128):
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

        self._buf = np.zeros([self._row_dim, self._col_dim, 2], dtype=np.uint8)
        self._prev_buf = np.zeros_like(self._buf)

        self._last_update = time.time()
        self._fps = 0.0

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
        self.set_sw_reset()         # Software reset
        time.sleep(0.15)

        self.set_sleep_control(1)   # Exit sleep mode
        time.sleep(0.5)
        
        self.set_color_mode(1)
        
        self.set_inversion(0)
        
        self.set_display_mode(1)    # Normal display mode
        
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
        if row_col == 0:   # col
            self._write_command(CASET)
        elif row_col == 1: # row
            self._write_command(RASET)
        else:
            raise ValueError('col = 0, row = 1')
        
        self._write_data([from_addr >> 8, from_addr & 0xFF, to_addr >> 8, to_addr & 0xFF])

    def _set_area(self, x0, y0, x1, y1):
        self._set_address(0, x0+2, x1+2) # col
        self._set_address(1, y0+1, y1+1) # row
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
        if x < 0 or x >= self._col_dim or y < 0 or y >= self._row_dim:
            #raise ValueError("pixel out of bound")
            return

        if color is None:
            color = self._brush_color

        self._buf[y, x] = [color >> 8, color & 0xFF]

    def draw_vertical_line(self, x, y, len_, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim or y+len_ > self._row_dim:
            raise ValueError("pixel out of bound")
        if len_ < 1:
            raise ValueError("len must be greater than 1")

        if color is None:
            color = self._brush_color
        
        self._buf[y:y+len_, x, 0] = color >> 8
        self._buf[y:y+len_, x, 1] = color & 0xFF

    def draw_horizontal_line(self, x, y, len_, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim or x+len_ > self._col_dim:
            raise ValueError("pixel out of bound")
        if len_ < 1:
            raise ValueError("len must be greater than 1")

        if color is None:
            color = self._brush_color
        
        self._buf[y, x:x+len_, 0] = color >> 8
        self._buf[y, x:x+len_, 1] = color & 0xFF

    def draw_rectangle(self, x, y, xlen, ylen, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim or x+xlen > self._col_dim or y+ylen > self._row_dim:
            raise ValueError("pixel out of bound")
        if xlen < 1 or ylen < 1:
            raise ValueError("lens must be greater than 1")

        if color is None:
            color = self._brush_color
        
        self._buf[y:y+ylen, x:x+xlen, 0] = color >> 8
        self._buf[y:y+ylen, x:x+xlen, 1] = color & 0xFF

    def draw_circle(self, x, y, radius, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim:
            raise ValueError("pixel out of bound")
        if color is None:
            color = self._brush_color
        
        for j in range(-radius, radius):
            for i in range(-radius, radius):
                if i**2 + j**2 < radius**2:
                    self.draw_pixel(x+i, y+j, color)

    def draw_sector(self, x, y, radius, start_angle, end_angle, color=None) -> None:
        if x < 0 or x > self._col_dim or y < 0 or y > self._row_dim:
            raise ValueError("pixel out of bound")
        if color is None:
            color = self._brush_color
        
        start_angle = start_angle % 360
        end_angle   = end_angle % 360

        for j in range(-radius, radius):
            for i in range(-radius, radius):
                if i**2 + j**2 < radius**2:
                    angle = math.degrees(math.atan2(-j, i))
                    angle = angle + 360 if angle < 0 else angle  # Normalize angle to [0, 360)
                    if start_angle <= end_angle:
                        if start_angle <= angle <= end_angle:
                            self.draw_pixel(x+i, y+j, color)
                    else:  # Crossing the 0-degree line
                        if angle >= start_angle or angle <= end_angle:
                            self.draw_pixel(x+i, y+j, color) 

    def draw_text(self, x, y, text, size, color=None) -> None:
        if x < 0 or x >= self._col_dim or y < 0 or y >= self._row_dim:
            raise ValueError("Pixel out of bound")

        if color is None:
            color = self._brush_color
        
        module_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(module_dir, 'arial.ttf')
        font = ImageFont.truetype(font_path, size)

        img  = Image.new("RGB", (len(text)*(size-4), size+4), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), text, font=font, fill=0xFFFFFF)

        img = img.convert("RGB")
        pixels = list(img.getdata())
        for j in range(img.height):
            for i in range(img.width):
                r, g, b = pixels[j*img.width+i]
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                if rgb565 != 0x0000:
                    self.draw_pixel(x+i, y+j, rgb565)

    def draw_image_from_path(self, x, y, width, height, path) -> None:
        if x < 0 or x >= self._col_dim or y < 0 or y >= self._row_dim:
            raise ValueError("Pixel out of bound")
        if (x + width > self._col_dim) or (y + height > self._row_dim):
            raise ValueError("Image exceeds display bounds")

        img = cv2.imread(path)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
        
        r = img[:, :, 2].astype(np.uint16) 
        g = img[:, :, 1].astype(np.uint16) 
        b = img[:, :, 0].astype(np.uint16) 
        color_map = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        self._buf[y:y+height, x:x+width, 0] = (color_map >> 8)
        self._buf[y:y+height, x:x+width, 1] = (color_map & 0xFF)

    # data: numpy array with shape = (y, x, depth) 
    def draw_image_from_data(self, x, y, width, height, data: np.ndarray) -> None:
        if x < 0 or x >= self._col_dim or y < 0 or y >= self._row_dim:
            raise ValueError("Pixel out of bound")
        if (x + width > self._col_dim) or (y + height > self._row_dim):
            raise ValueError("Image exceeds display bounds")
        
        data = cv2.resize(data, (width, height), interpolation=cv2.INTER_AREA)
        r = data[:, :, 2].astype(np.uint16)
        g = data[:, :, 1].astype(np.uint16)
        b = data[:, :, 0].astype(np.uint16)
        color_map = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        self._buf[y:y+height, x:x+width, 0] = (color_map >> 8)
        self._buf[y:y+height, x:x+width, 1] = (color_map & 0xFF)

    def fill_screen(self, color) -> None:
        if color is None:
            color = self._background_color
        self.draw_rectangle(0, 0, self._col_dim, self._row_dim, color)

    def clear(self) -> None:
        self._buf = np.zeros((self._row_dim, self._col_dim, 2), dtype=np.uint8)

    def update(self) -> None:
        self._fps = 1/(time.time()-self._last_update)
        self._set_area(0, 0, self._col_dim-1, self._row_dim-1)
        for i in range(0, len(self._buf.flatten()), self._chunksize):
            self._write_data(self._buf.flatten()[i:i+self._chunksize].tolist())
        self._last_update = time.time()

    def get_fps(self) -> float:
        return self._fps

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    screen = Screen(col_dim=128, row_dim=160)
    screen.clear()

    img = cv2.imread("./google.jpg")
    while 1:
        
        screen.draw_pixel(0, 0, RGB565Color.WHITE)
        screen.draw_pixel(1, 0, RGB565Color.WHITE)
        screen.draw_pixel(0, 1, RGB565Color.WHITE)
        screen.draw_pixel(1, 1, RGB565Color.WHITE)
        screen.draw_pixel(0, screen.get_row_dim()-1)
        screen.draw_pixel(screen.get_col_dim()-1, 0)
        screen.draw_pixel(screen.get_col_dim()-1, screen.get_row_dim()-1)
        
        screen.draw_vertical_line(15, 15, 10)
        screen.draw_horizontal_line(30, 10, 20)
        screen.draw_rectangle(10, 35, 20, 20, RGB565Color.PINK)
        
        screen.draw_circle(90, 20, 20, RGB565Color.BLUE)
        screen.draw_sector(40, 30, 25, -45, 45, RGB565Color.ORANGE)
        
        #screen.draw_image_from_path(44, 64, 40, 40, "./google.jpg")
        screen.draw_text(20, 120, "Google HPS 2024", 12, RGB565Color.WHITE)
        screen.draw_image_from_data(44, 64, 40, 40, img)
        
        colorlist = [RGB565Color.BLACK, RGB565Color.WHITE, RGB565Color.BLUE, RGB565Color.RED, 
                     RGB565Color.GREEN, RGB565Color.ORANGE, RGB565Color.YELLOW, RGB565Color.PINK, 
                     RGB565Color.CYAN, RGB565Color.VIOLET]
        for index, color in enumerate(colorlist):
            screen.draw_rectangle(10+index*10, 151, 10, 8, color)
        screen.draw_horizontal_line(10, 151, 100, RGB565Color.WHITE)
        screen.draw_horizontal_line(10, 159, 100, RGB565Color.WHITE)
        screen.draw_vertical_line(10, 151, 9, RGB565Color.WHITE)
        screen.draw_vertical_line(110, 151, 9, RGB565Color.WHITE)
        
        screen.draw_text(0, 0, "FPS: {:.2f}".format(screen.get_fps()), 10, RGB565Color.CYAN)
        
        screen.update()
        screen.clear()

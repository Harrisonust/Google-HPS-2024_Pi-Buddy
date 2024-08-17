import pygame
import sys

class Screen:
    def __init__(self):
        self.col_dim = 128
        self.row_dim = 128
        self.brush_color = (0, 0, 0)
        self.fps = None
        self.screen = None
    
    def _start_screen(self):
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.row_dim, self.col_dim))
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption("Test Screen")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    
    def get_col_dim(self):
        return self.col_dim
    
    def get_row_dim(self):
        return self.row_dim
    
    # What's this?
    def set_sw_reset(self):
        pass
        
    # What's this?
    def set_sleep_control(self, in_out):
        pass
        
    # What's this?
    def set_color_mode(self, color_mode):
        pass
    
    # What's this?
    def set_display_mode(self, mode):
        pass
   
    # What's this?
    def set_inversion(self, on_off):
        pass
    
    def set_brush_color(self, color):
        self.brush_color = color
    
    def set_background_color(self, color):
        pass
    
    def draw_pixel(self, x, y, color=None):
        color = self.color if (color == None) else color
        pygame.draw.line(self.screen, color, (x, y), (x, y), 1)

    def draw_vertical_line(self, x, y, len_, color=None):
        color = self.color if (color == None) else color
        pygame.draw.line(self.screen, color, (x, y), (x, y + len_), 5)
    
    def draw_horizontal_line(self, x, y, len_, color=None):
        color = self.color if (color == None) else color
        pygame.draw.line(self.screen, color, (x, y), (x + len_, y), 5)
    
    def draw_rectangle(self, x, y, xlen, ylen, color=None):
        color = self.color if (color == None) else color
        pygame.draw.rect(self.screen, color, (x, y, xlen, ylen))
    
    def draw_circle(self, x, y, radius, color=None):
        color = self.color if (color == None) else color
        pygame.draw.circle(self.screen, color, (x, y), radius, 0)
    
    # What's this?
    def draw_sector(self, x, y, radius, start_angle, end_angle, color=None):
        pass
    
    def draw_text(self, x, y, text, size, color=None):
        pass
    
    def draw_image(self, x, y, width, height, path):
        pass
    
    def fill_screen(self, color):
        self.screen.fill(color)
    
    # What's this?
    def clear(self):
        pass
    
    def update(self):
        pass
    
    # What's this?
    def get_fps(self):
        pass

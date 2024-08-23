import time
from enum import Enum
import RPi.GPIO as GPIO

from components.st7735s.st7735s import Screen
from handlers.handler import Handler
from value_manager import ValueManager
from pages import *

from pin_defines import *

# PageId indexes
class PageId:
    MenuPage = 0
    SetTimerPage = 1 
    TimerPage = 2
    TimePage = 3
    WeatherPage = 4
    TodoPage = 5
    #PhotographPage = 6
    #FilmPage = 7
    BatteryPage = 6
    

class MenuScreenHandler(Handler):
    def __init__(self, task_queue, debug=False):
        self.debug = debug

        self.run_input_process = False
        self.task_queue = task_queue
        
        self.screen = Screen(col_dim=160, row_dim=128, pin_dc=PIN_LCD_DC, pin_rst=PIN_LCD_RST)
        self.screen.clear()
        
        self.pages = [
            MenuPage(self.screen),
            SetTimerPage(self.screen),
            TimerPage(self.screen),
            TimePage(self.screen),
            WeatherPage(self.screen),
            TodoPage(self.screen),
            #PhotographPage(self.screen),
            #FilmPage(self.screen),
            BatteryPage(self.screen)
        ]
        
        self.menu_screen_handler_busy = ValueManager(int(False))
        
        self.current_page_id = ValueManager(PageId.MenuPage)
        # self.current_page_id = ValueManager(PageId.SetTimerPage)
        # self.current_page_id = ValueManager(PageId.TimerPage)
        # self.current_page_id = ValueManager(PageId.TimePage)
        # self.current_page_id = ValueManager(PageId.WeatherPage)
        # self.current_page_id = ValueManager(PageId.TodoPage)        
        # self.current_page_id = ValueManager(PageId.PhotographPage)
        # self.current_page_id = ValueManager(PageId.BatteryPage)
        
        
        self.current_page_priority = ValueManager(0)
        
        self.pages[self.current_page_id.reveal()].start_display()
        
    
    def listen(self):
        raise TypeError(f'Invalid call to ScreenHandler "listen" function')
    
    
    def handle_task(self, task_info):
        if self.menu_screen_handler_busy.reveal():
            self.task_queue.append(task_info)
        
        else:
            self.menu_screen_handler_busy.overwrite(int(True))
            new_page_info = self.pages[self.current_page_id.reveal()].handle_task(task_info)

            if new_page_info:
                new_page, msg_to_new_page = new_page_info         
                if new_page == 'MenuPage':
                    self.current_page_id.overwrite(PageId.MenuPage)
                    
                elif new_page == 'SetTimerPage':
                    self.current_page_id.overwrite(PageId.SetTimerPage)
                    
                elif new_page == 'TimerPage':
                    self.current_page_id.overwrite(PageId.TimerPage)
                
                elif new_page == 'TimePage':
                    self.current_page_id.overwrite(PageId.TimePage)
                    
                elif new_page == 'WeatherPage':
                    self.current_page_id.overwrite(PageId.WeatherPage)
                
                elif new_page == 'TodoPage':
                    self.current_page_id.overwrite(PageId.TodoPage)
                
                elif new_page == 'PhotographPage':
                    self.current_page_id.overwrite(PageId.PhotographPage)
                
                elif new_page == 'FilmPage':
                    self.current_page_id.overwrite(PageId.FilmPage)
                    
                elif new_page == 'BatteryPage':
                    self.current_page_id.overwrite(PageId.BatteryPage)
                
                current_page_id = self.current_page_id.reveal()
                self.pages[current_page_id].reset_states(msg_to_new_page)
                self.pages[current_page_id].start_display()
                        
            self.menu_screen_handler_busy.overwrite(int(False))
        



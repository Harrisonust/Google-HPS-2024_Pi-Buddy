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
    EmotionPage =       0
    MenuPage =          1
    SetTimerPage =      2 
    TimerPage =         3
    TimePage =          4
    WeatherPage =       5
    TodoPage =          6
    BatteryPage =       7
    PhotographPage =    8
    FilmPage =          9
    

class MenuScreenHandler(Handler):
    def __init__(self, task_queue):

        self.run_input_process = False
        self.task_queue = task_queue
        
        self.screen = Screen(col_dim=160, row_dim=128, pin_dc=PIN_LCD_DC, pin_rst=PIN_LCD_RST)
        self.screen.clear()
        
        self.page_id2key = {
            PageId.EmotionPage:     'EmotionPage',
            PageId.MenuPage:        'MenuPage',
            PageId.SetTimerPage:    'SetTimerPage',
            PageId.TimerPage:       'TimerPage',
            PageId.TimePage:        'TimePage',
            PageId.WeatherPage:     'WeatherPage',
            PageId.TodoPage:        'TodoPage',
            PageId.BatteryPage:     'BatteryPage',
            PageId.PhotographPage:  'PhotographyPage',
            PageId.FilmPage:        'FilmPage',
        }
        
        self.page_key2id = {
            'EmotionPage':          PageId.EmotionPage,
            'MenuPage':             PageId.MenuPage,
            'SetTimerPage':         PageId.SetTimerPage,
            'TimerPage':            PageId.TimerPage,
            'TimePage':             PageId.TimePage,
            'WeatherPage':          PageId.WeatherPage,
            'TodoPage':             PageId.TodoPage,
            'BatteryPage':          PageId.BatteryPage,
            'PhotographPage':       PageId.PhotographPage,
            'FilmPage':             PageId.FilmPage,
        }
        
        self.pages = {
            'EmotionPage':          EmotionPage(self.screen),
            'MenuPage':             MenuPage(self.screen),
            'SetTimerPage':         SetTimerPage(self.screen),
            'TimerPage':            TimerPage(self.screen),
            'TimePage':             TimePage(self.screen),
            'WeatherPage':          WeatherPage(self.screen),
            'TodoPage':             TodoPage(self.screen),
            'BatteryPage':          BatteryPage(self.screen),
            # 'PhotographPage':       PhotographPage(self.screen),
            # 'FilmPage':             FilmPage(self.screen),
        }
        
        self.menu_screen_handler_busy = ValueManager(int(False))
        self.current_page_priority = ValueManager(0)
        self.current_page_id = ValueManager(PageId.EmotionPage)
        
        # self.current_page_id = ValueManager(PageId.MenuPage)
        # self.current_page_id = ValueManager(PageId.SetTimerPage)
        # self.current_page_id = ValueManager(PageId.TimerPage)
        # self.current_page_id = ValueManager(PageId.TimePage)
        # self.current_page_id = ValueManager(PageId.WeatherPage)
        # self.current_page_id = ValueManager(PageId.TodoPage)        
        # self.current_page_id = ValueManager(PageId.PhotographPage)
        # self.current_page_id = ValueManager(PageId.BatteryPage)
        
        
        
        self.pages[self.page_id2key[self.current_page_id.reveal()]].start_display()
        
    
    def listen(self):
        raise TypeError(f'Invalid call to ScreenHandler "listen" function')
    
    
    def handle_task(self, task_info):
        if self.menu_screen_handler_busy.reveal():
            self.task_queue.append(task_info)
        
        else:
            self.menu_screen_handler_busy.overwrite(int(True))
            return_values = self.pages[self.page_id2key[self.current_page_id.reveal()]].handle_task(task_info)

            if return_values is not None:
                if return_values['type'] == 'NEW_TASK':
                    self.task_queue.append(return_values['task'])
                    
                elif return_values['type'] == 'NEW_PAGE':
                    self.current_page_id.overwrite(self.page_key2id[return_values['page']])
                    current_page_id = self.current_page_id.reveal()
                    current_page_key = self.page_id2key[current_page_id]
                    self.pages[current_page_key].reset_states(return_values['args'])
                    self.pages[current_page_key].start_display()
                        
            self.menu_screen_handler_busy.overwrite(int(False))
        



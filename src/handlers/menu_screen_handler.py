import time
from enum import Enum
import RPi.GPIO as GPIO

from components.st7735s.st7735s import Screen
from handlers.handler import Handler
from value_manager import ValueManager
from pages import *


# PageId indexes
class PageId:
    MenuPage = 0
    SetTimerPage = 1 
    TimerPage = 2
    TimePage = 3

class MenuScreenHandler(Handler):
    def __init__(self, task_queue, debug=False):
        self.debug = debug

        self.run_input_process = False
        self.task_queue = task_queue
        
        GPIO.setmode(GPIO.BCM)
        self.screen = Screen(col_dim=160, row_dim=128)
        self.screen.clear()
        
        self.pages = [
            MenuPage(self.screen),
            SetTimerPage(self.screen),
            TimerPage(self.screen),
            TimePage(self.screen)
        ]
        
        self.menu_screen_handler_busy = ValueManager(int(False))
        
        # self.current_page_id = ValueManager(PageId.SetTimerPage)
        # self.current_page_id = ValueManager(PageId.MenuPage)
        # self.current_page_id = ValueManager(PageId.TimerPage)
        self.current_page_id = ValueManager(PageId.TimePage)
        
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
                    print('B time page')
                    self.current_page_id.overwrite(PageId.TimePage)
                
                current_page_id = self.current_page_id.reveal()
                self.pages[current_page_id].reset_states(msg_to_new_page)
                self.pages[current_page_id].start_display()
                        
            self.menu_screen_handler_busy.overwrite(int(False))
        



import time
from enum import Enum
import RPi.GPIO as GPIO

from components.st7735s.st7735s import Screen
from handlers.handler import Handler
from value_manager import ValueManager
from pages import *


class MenuScreenHandler(Handler):
    def __init__(self, task_queue, debug=False):
        self.debug = debug

        self.run_input_process = False
        self.task_queue = task_queue
        
        self.screen = Screen(col_dim=160, row_dim=128)
        self.screen.clear()
        self.page = SetTimerPage(self.screen)

        self.menu_screen_handler_busy = ValueManager(int(False))
        self.current_page_id = ValueManager(0)
        self.current_page_priority = ValueManager(0)
        
    
    def listen(self):
        raise TypeError(f'Invalid call to ScreenHandler "listen" function')
    
    
    def handle_task(self, task_info):
        if self.menu_screen_handler_busy.reveal():
            self.task_queue.append(task_info)
        
        else:
            self.menu_screen_handler_busy.overwrite(int(True))
            new_page = self.page.handle_task(task_info)
            
            if new_page:
                
                if new_page == 'Menu':
                    self.page = MenuPage(self.screen)
                elif new_page == 'Timer':
                    self.page = SetTimerPage(self.screen)

                        
            self.menu_screen_handler_busy.overwrite(int(False))
        



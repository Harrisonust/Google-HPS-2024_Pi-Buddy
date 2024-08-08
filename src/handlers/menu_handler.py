import time
from enum import Enum

from components.st7735s import Screen
from handlers.handler import Handler
from value_manager import ValueManager
from pages import *


# class MenuManager:
#     def __init__(self):
#         self.pages = {}
#         self.current_page = None
#         self.current_page_priority = ValueManager(0)
        
#     def 

#     def set_current_page(self, page_name):
#         self.current_page = self.pages.get(page_name)

#     def get_current_page(self):
#         return self.current_page

#     def navigate(self, direction):
#         self.current_page.navigate(direction)

#     def select(self):
#         self.current_page.select()


class MenuScreenHandler(Handler):
    def __init__(self, task_queue, debug=False):
        self.debug = debug

        self.run_input_process = False
        self.task_queue = task_queue
        
        
        self.screen = Screen()
        self.pages = [
            MenuPage(),
            TimerPage(),
            WeatherPage(),
        ]

        self.screen_busy = ValueManager(int(False))
        self.current_page_id = ValueManager(0)
        self.current_page_priority = ValueManager(0)
        
    
    def listen(self):
        raise TypeError(f'Invalid call to ScreenHandler "listen" function')
    
    
    def handle_task(self, task_info):
        if self.screen_busy.reveal():
            self.task_queue.append(task_info)
        
        else:
            self.screen_busy.overwrite(int(True))
            self.pages[self.current_page_id].handle_task(task_info)
            self.screen_busy.overwrite(int(False))
        

    def display(self):
        current_page = self.menu_manager.get_current_page()
        current_page.render()


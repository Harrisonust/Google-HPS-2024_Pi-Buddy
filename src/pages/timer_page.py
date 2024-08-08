import time
from enum import Enum


from pages.page import Page
from value_manager import ValueManager


timer_state_active_buttons = {
    'TIMER_SETTING': ['hr_h', 'hr_l', 'min_h', 'min_l', 'sec_h', 'sec_l', 'set'],
    'TIMER_SET': ['reset', 'start'],
    'TIMER_RUNNING': ['reset', 'pause', 'restart'],
    'TIMER_PAUSED': ['reset', 'continue', 'restart']
}    

class TimerPage(Page):
    def __init__(self):
        self.timer_state = 'TIMER_SETTING'
        self.cursor_location_id = 0
        self.cursor_enabled = True
        self.count_down_running = False

        # Time values currently displayed on screen
        self.time_val_cur = {
            'hr_h': 0,
            'hr_l': 0,
            'min_h': 0,
            'min_l': 0,
            'sec_h': 0,
            'sec_l': 0
        }
        
        # Time values set by user
        self.time_val_set = {
            'hr_h': 0,
            'hr_l': 0,
            'min_h': 0,
            'min_l': 0,
            'sec_h': 0,
            'sec_l': 0
        }
        
        self.time_val_max_range = {
            'hr_h': 10,
            'hr_l': 10,
            'min_h': 6,
            'min_l': 10,
            'sec_h': 6,
            'sec_l': 10
        }
    
    def handle_task(self, task_info):
        if task_info['task'] == 'ENTER':
            selected = timer_state_active_buttons[self.timer_state][self.cursor_location_id]
            if selected == 'set':
                for key in self.time_val_cur:
                    self.time_val_set[key] = self.time_val_cur[key]
                self.timer_state = 'TIMER_SET'
            elif selected == 'reset':
                self.timer_state = 'TIMER_SETTING'
            elif selected == 'start':
                self.timer_state = 'TIMER_RUNNING'
            elif selected == 'pause':
                self.timer_state = 'TIMER_PAUSED'
            elif selected == 'continue':
                self.timer_state = 'TIMER_RUNNING'
            elif selected == 'restart':
                for key in self.time_val_set:
                    self.time_val_cur[key] = self.time_val_set[key]
                self.timer_state = ''
            
        elif task_info['task'] == 'RESUME':
            pass
        
        elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
            if self.cursor_enabled:
                self.cursor_location_id += 1
                self.cursor_location_id = self.cursor_location_id % len(timer_state_active_buttons[self.timer_state])
            else:
                selected = timer_state_active_buttons[self.timer_state][self.cursor_location_id]
                self.time_val_cur[selected] = (self.time_val_cur[selected] + 1) % self.time_val_max_range[selected]
                    
        elif task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
            if self.cursor_enabled:
                self.cursor_location_id -= 1
                self.cursor_location_id = self.cursor_location_id % len(timer_state_active_buttons[self.timer_state])
            else:
                selected = timer_state_active_buttons[self.timer_state][self.cursor_location_id]
                self.time_val_cur[selected] = (self.time_val_cur[selected] - 1) % self.time_val_max_range[selected]
            
    
    def paint(self):
        pass
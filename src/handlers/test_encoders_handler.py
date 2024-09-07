import time
import threading
import sqlite3

from value_manager import ValueManager
from handlers.handler import Handler


class TestEncodersHandler(Handler):
    
    def __init__(self, task_queue):
        self.run_input_process = False
        self.task_queue = task_queue
        
        self.task_updated = ValueManager(int(False))

        listen_key_input_thread = threading.Thread(target=self._listen_key_input)
        listen_key_input_thread.start()
        
        timer_thread = threading.Thread(target=self._timer)
        timer_thread.start()
    
    
    def _timer(self):
        # A timer to keep track of how long there had been no tasks from the encoder
        timer_start = time.time()
        time_with_no_encoder_updates = 0
        while True:
            
            if self.task_updated.reveal():
                timer_start = time.time()
                self.task_updated.overwrite(int(False))
            
            time_with_no_encoder_updates = time.time() - timer_start
            
            if time_with_no_encoder_updates > 10:
                timer_start = time.time()
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'PAGE_EXPIRED',
                    'task_priority': 1
                })
            
            time.sleep(0.5)
            
    
    
    def _listen_key_input(self):
        while True:
            user_input = input('move_cursor_left_down(a)/move_cursor_right_up(d)/enter_select(s)/out_resume(w):')
            if user_input == 'a':
                self.task_updated.overwrite(int(True))
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'MOVE_CURSOR_LEFT_DOWN',
                    'task_priority': 1
                })
            
            elif user_input == 'd':
                self.task_updated.overwrite(int(True))
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'MOVE_CURSOR_RIGHT_UP',
                    'task_priority': 1
                })
            
            elif user_input == 's':
                self.task_updated.overwrite(int(True))
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'ENTER_SELECT',
                    'task_priority': 1
                })
            
            elif user_input == 'w':
                self.task_updated.overwrite(int(True))
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'OUT_RESUME',
                    'task_priority': 1
                })
            
            elif user_input == 't':
                self.task_updated.overwrite(int(True))
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'audio',
                    'task': 'FUNCTION_CALLED',
                })
            
        
        time.sleep(0.01)
    
    def listen(self):
        pass
    
    def handle_task(self):
        raise TypeError(f'Invalid call to EncodersHandler "handle_task" function')
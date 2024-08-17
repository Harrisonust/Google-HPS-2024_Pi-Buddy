import time
import threading

from value_manager import ValueManager
from handlers.handler import Handler


class TestEncodersHandler(Handler):
    
    def __init__(self, task_queue, debug=False):
        self.run_input_process = False
        self.task_queue = task_queue

        listen_key_input_thread = threading.Thread(target=self._listen_key_input)
        listen_key_input_thread.start()
    
    def _listen_key_input(self):
        while True:
            user_input = input('move_cursor_left_down(a)/move_cursor_right_up(d)/enter_select(s)/out_resume(w):')
            if user_input == 'a':
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'MOVE_CURSOR_LEFT_DOWN',
                    'task_priority': 1
                })
            
            elif user_input == 'd':
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'MOVE_CURSOR_RIGHT_UP',
                    'task_priority': 1
                })
            
            elif user_input == 's':
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'ENTER_SELECT',
                    'task_priority': 1
                })
            
            elif user_input == 'w':
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'OUT_RESUME',
                    'task_priority': 1
                })
    
    def listen(self):
        pass
    
    def handle_task(self):
        raise TypeError(f'Invalid call to EncodersHandler "handle_task" function')
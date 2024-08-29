import time

from handlers.handler import Handler
from value_manager import ValueManager




class AudioHandler(Handler):
    
    def __init__(self, task_queue):
        self.run_input_process = True
        self.task_queue = task_queue
        
        
    def listen(self):
        while True:
            print('in listen() while true loop')
            time.sleep(0.5)
    
    

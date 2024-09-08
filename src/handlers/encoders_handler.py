import time
import threading

from components.encoder import Encoder
from handlers.handler import Handler
from value_manager import ValueManager
from pin_defines import *


class EncoderConfig:
    READ_PERIOD = 0.1       # Define the period to read left and right encoder positions
    VALID_DISPLACEMENT = 1  # Define the threshold for valid displacement
    EXPIRATION_TIME = 20    # Time capacity before expiration signal is sent
    

class EncodersHandler(Handler):
    def __init__(self, task_queue):
        self.run_input_process = True
        self.task_queue = task_queue
        
        # Encoder initialization
        self.glide_encoder = Encoder(PIN_MENU_ENC1A, PIN_MENU_ENC1B)
        self.select_encoder = Encoder(PIN_MENU_ENC2B, PIN_MENU_ENC2A)
        
        self.glide_encoder_prev_pos = self.glide_encoder.get_position()
        self.select_encoder_prev_pos = self.select_encoder.get_position()
        
        # Timer initialization
        self.task_updated = ValueManager(int(False))
        
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
            
            if time_with_no_encoder_updates > EncoderConfig.EXPIRATION_TIME:
                # print('time expiration!')
                timer_start = time.time()
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'PAGE_EXPIRED',
                    'task_priority': 1
                })
            
            time.sleep(0.5)
        
    
    def listen(self):
        
        while True:
            # Get cur_pos values
            glide_encoder_cur_pos = self.glide_encoder.get_position()
            select_encoder_cur_pos = self.select_encoder.get_position()

            if select_encoder_cur_pos - self.select_encoder_prev_pos >= EncoderConfig.VALID_DISPLACEMENT:
                print(f"Glide: {glide_encoder_cur_pos}, Select: {select_encoder_cur_pos}")
                # ENTER_SELECT
                self.task_updated.overwrite(int(True))
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'ENTER_SELECT',
                    'task_priority': 1
                })
            
            elif self.select_encoder_prev_pos - select_encoder_cur_pos >= EncoderConfig.VALID_DISPLACEMENT:
                print(f"Glide: {glide_encoder_cur_pos}, Select: {select_encoder_cur_pos}")
                # OUT_RESUME
                self.task_updated.overwrite(int(True))
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'OUT_RESUME',
                    'task_priority': 1
                })
            
            elif glide_encoder_cur_pos - self.glide_encoder_prev_pos >= EncoderConfig.VALID_DISPLACEMENT:
                print(f"Glide: {glide_encoder_cur_pos}, Select: {select_encoder_cur_pos}")
                # MOVE_CURSOR_RIGHT_UP
                self.task_updated.overwrite(int(True))
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'MOVE_CURSOR_RIGHT_UP',
                    'task_priority': 1
                })
            
                print(f"Glide: {glide_encoder_cur_pos}, Select: {select_encoder_cur_pos}")
            elif self.glide_encoder_prev_pos - glide_encoder_cur_pos >= EncoderConfig.VALID_DISPLACEMENT:
                print(f"Glide: {glide_encoder_cur_pos}, Select: {select_encoder_cur_pos}")
                self.task_updated.overwrite(int(True))
                self.task_queue.append({
                    'requester_name': 'encoders',
                    'handler_name': 'menu_screen',
                    'task': 'MOVE_CURSOR_LEFT_DOWN',
                    'task_priority': 1
                })
            
            else:
                # NO ACTION
                pass
            
            # Update prev_pos values from cur_pos values
            self.glide_encoder_prev_pos = glide_encoder_cur_pos
            self.select_encoder_prev_pos = select_encoder_cur_pos
            
            time.sleep(EncoderConfig.READ_PERIOD)        
    
    def handle_task(self):
        # handle_task should not be called on for EncodersHandler
        raise TypeError(f'Invalid call to EncodersHandler "handle_task" function')

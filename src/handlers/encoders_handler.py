import time
from enum import Enum

from components.encoder import Encoder
from handlers.handler import Handler
from value_manager import ValueManager


class EncoderConfig(Enum):
    READ_PERIOD = 0.01      # Define the period to read left and right encoder positions
    VALID_DISPLACEMENT = 5  # Define the threshold for valid displacement


class EncodersHandler(Handler):
    def __init__(self, task_queue, debug=False):
        self.debug = debug
        
        self.run_input_process = True
        self.task_queue = task_queue
        
        
        self.glide_encoder = Encoder(0, 5)
        self.select_encoder = Encoder(0, 5)
        
        self.glide_encoder_prev_pos = self.glide_encoder.get_position()
        self.select_encoder_prev_pos = self.select_encoder.get_position()
        
    
    def listen(self):
        
        while True:
            # Get cur_pos values
            glide_encoder_cur_pos = self.glide_encoder.get_position()
            select_encoder_cur_pos = self.select_encoder.get_position()
            
            if select_encoder_cur_pos - self.select_encoder_prev_pos > EncoderConfig.VALID_DISPLACEMENT.value:
                # ENTER SELECTED
                # self.task_queue.append({
                #     'requester_name': 'encoders',
                #     'handler_name': 'menu',
                #     'task': 'ENTER_SELECT',
                #     'task_priority': 1
                # })
                pass
            
            elif self.select_encoder_prev_pos - select_encoder_cur_pos > EncoderConfig.VALID_DISPLACEMENT.value:
                # RESUME
                # self.task_queue.append({
                #     'requester_name': 'encoders',
                #     'handler_name': 'menu',
                #     'task': 'OUT_RESUME',
                #     'task_priority': 1
                # })
                pass
            
            elif glide_encoder_cur_pos - self.glide_encoder_prev_pos > EncoderConfig.VALID_DISPLACEMENT.value:
                # MOVE CURSOR RIGHT/UP
                # self.task_queue.append({
                #     'requester_name': 'encoders',
                #     'handler_name': 'menu',
                #     'task': 'MOVE_CURSOR_RIGHT_UP',
                #     'task_priority': 1
                # })
                pass
            
            elif self.glide_encoder_prev_pos - glide_encoder_cur_pos > EncoderConfig.VALID_DISPLACEMENT.value:
                # MOVE CURSOR LEFT/DOWN
                # self.task_queue.append({
                #     'requester_name': 'encoders',
                #     'handler_name': 'menu',
                #     'task': 'MOVE_CURSOR_LEFT_DOWN',
                #     'task_priority': 1
                # })
                pass
            
            else:
                # NO ACTION
                pass
            
            # Update prev_pos values from cur_pos values
            self.glide_encoder_prev_pos = glide_encoder_cur_pos
            self.select_encoder_prev_pos = select_encoder_cur_pos
            
            time.sleep(EncoderConfig.READ_PERIOD.value)        
    
    def handle_task(self):
        # handle_task should not be called on for EncodersHandler
        raise TypeError(f'Invalid call to EncodersHandler "handle_task" function')
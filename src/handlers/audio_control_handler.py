from handlers.handler import Handler
from value_manager import ValueManager


class AudioControlHandler(Handler):
    
    def __init__(self, task_queue):
        self.run_input_process = True
        self.task_queue = task_queue
    
    
    def page_switching(self, page, args):
        self.task_queue.append_task({
            'requester_name': 'audio_control',
            'handler_name': 'menu_screen',
            'task': 'SWITCH_PAGE',
            'page_key': page + 'Page',
            'args': args
        })
    
    
    def call_and_come(self):
        pass
    

    def set_emotion(self, emotion):
        self.task_queue.append_task({
            'requester_name': 'audio_control',
            'handler_name': 'emotion',
            'task': 'SET_EMOTION',
            'args': emotion,
        })

    
    def set_count_down_timer(self, seconds_to_count_down=None, minutes_to_count_down=None, hours_to_count_down=None):
        if seconds_to_count_down == None and minutes_to_count_down == None and hours_to_count_down == None:
            raise ValueError("Error: arguments cannnot all be 'None' for 'set_count_down_timer'")
        self.page_switching('Timer', seconds_to_count_down)

    
    def add_todo(self, task_name):
        pass


    def take_a_photo(self):
        self.page_switching('Photo', )

    
    def start_recording(self):
        self.page_switching('Film', )

    
    def end_recording(self):
        self.page_switching('Film', )
    
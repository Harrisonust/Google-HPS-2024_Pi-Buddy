import sqlite3

from handlers.handler import Handler
from value_manager import ValueManager
from pages.pages_utils import PageConfig


class AudioControlHandler(Handler):
    
    def __init__(self, task_queue):
        self.run_input_process = False
        self.task_queue = task_queue
        
        
        ### FOR DEBUGGING & TESTING ###
        self.function_in_test = self.add_todo
        self.args_to_function_in_test = ('Finish Photopage',)
        
        self.task_handler_busy = ValueManager(int(False))

        ### FOR DEBUGGING & TESTING ###
    
    def handle_task(self, task_info):
        if not self.task_handler_busy.reveal():
            self.task_handler_busy.overwrite(int(True))
        
            if task_info['task'] == 'FUNCTION_CALLED':
                self.function_in_test(*self.args_to_function_in_test)
        
            self.task_handler_busy.overwrite(int(False))
    
    
    def page_switching(self, page, args=None):
        # 1 
        print(f'page = {page}, args = {args}')
        # If no arguments are given, and the page is 'Timer', go to the 'SetTimer' page
        if page == 'Timer':
            if args == None:
                page = 'SetTimer'
            else:
                args = self._get_time_val(
                    seconds_to_count_down = args[0]
                )
        
        self.task_queue.append({
            'requester_name': 'audio_control',
            'handler_name': 'menu_screen',
            'task': 'SWITCH_PAGE',
            'page_key': page + 'Page',
            'args': args
        })
    
    
    def call_and_come(self):
        # -1
        pass
    

    def set_emotion(self, emotion):
        # 3
        self.task_queue.append({
            'requester_name': 'audio_control',
            'handler_name': 'emotion',
            'task': 'SET_EMOTION',
            'args': emotion,
        })

    
    def set_count_down_timer(self, seconds_to_count_down=0, minutes_to_count_down=0, hours_to_count_down=0):
        # 2
        if seconds_to_count_down == 0 and minutes_to_count_down == 0 and hours_to_count_down == 0:
            raise ValueError("Error: arguments cannnot all be 'None' for 'set_count_down_timer'")
        
        minutes_to_count_down += hours_to_count_down * 60
        seconds_to_count_down += minutes_to_count_down * 60
        self.page_switching('Timer', (seconds_to_count_down,))

    
    def add_todo(self, task_name):
        # 5
        self._write_todo_task(task_name)
        
        self.task_queue.append({
            'requester_name': 'audio_control',
            'handler_name': 'menu_screen',
            'task': 'RELOAD_TODO_TASK',
        })


    def take_a_photo(self):
        # 4
        self.page_switching('Photograph', 'take_photo')

    
    def start_recording(self):
        # 4
        self.page_switching('Film', 'start_recording')

    
    def end_recording(self):
        # 4
        self.task_queue.append({
            'requester_name': 'audio_control',
            'handler_name': 'menu_screen',
            'task': 'END_RECORDING',
        })
    
    
    def _get_time_val(self, seconds_to_count_down=0, minutes_to_count_down=0, hours_to_count_down=0):
        minutes_to_count_down += seconds_to_count_down // 60
        seconds_to_count_down %= 60
        hours_to_count_down += minutes_to_count_down // 60
        minutes_to_count_down %= 60
        hours_to_count_down %= 100
        
        return {
            'hr_h':  hours_to_count_down // 10,
            'hr_l':  hours_to_count_down % 10,
            'min_h': minutes_to_count_down // 10,
            'min_l': minutes_to_count_down % 10,
            'sec_h': seconds_to_count_down // 10,
            'sec_l': seconds_to_count_down % 10
        }
    
    def _write_todo_task(self, task_name):
        self.conn = sqlite3.connect(PageConfig.DB_PATH)
        self.cursor = self.conn.cursor()
        
        try:
            self.cursor.execute(
                f'''
                INSERT INTO todo (task_name, is_active)
                VALUES           ('{task_name}', 1);
                '''
            )
            self.conn.commit()
        
        except Exception as e:
            print(f'An error occurred: {e}')
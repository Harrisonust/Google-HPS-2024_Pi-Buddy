# import multiprocessing
import threading, queue
import RPi.GPIO as GPIO
import time

from handlers import *
from database.reset_database import reset_db


class TaskQueue:
    def __init__(self):
        # Use a multiprocessing manager to create a shared list for tasks
        self.tasks = queue.Queue()
        # Create a lock to synchronize access to the task queue
        self.lock = threading.Lock()
    
    def append(self, task_info):
        # Append a new task to the task queue in a safe manner
        with self.lock:
            self.tasks.put(task_info)
            return True
    
    def pop(self):
        # Pop a task from the task queue in a safe manner
        with self.lock:
            if self.tasks:
                return self.tasks.get()
            return None
        
    def get_len(self):
        # Get the length of the task queue in a safe manner
        with self.lock:
            return self.tasks.qsize()


class Control:
    def __init__(self, reset_database=False):
        
        # Initialize the task queue
        self.task_queue = TaskQueue()
        
        
        # Initialize handlers and pass the task queue to them
        self.handlers = {
            'battery': BatteryHandler(self.task_queue),
            'encoders': EncodersHandler(self.task_queue),
            'menu_screen': MenuScreenHandler(self.task_queue),
            'emotion': EmotionHandler(self.task_queue),
            'audio': AudioHandler(self.task_queue),
            'robot_movement': RobotMovementHandler(self.task_queue),
            #'teleop': TeleopHandler(self.task_queue),
        }

        
        if reset_database:
            reset_db(reset_todo=False, reset_images=True, reset_videos=True)
    
        # Start listening processes for each handler
        self._start_listening()
        
        # Stat a process to execute tasks from the queue 
        self._execute_tasks()
        process = threading.Thread(target=self._execute_tasks)
        process.name = 'main execute task'
        process.start()
       
        for thread in threading.enumerate():
            print(thread.name)


    def _start_listening(self):
        # Start listening processes for input handlers
        for handler_name in self.handlers:
            handler = self.handlers[handler_name]
            if handler.run_input_process:
                process = threading.Thread(target=handler.listen)
                process.name = f'{handler_name} listen'
                process.start()


    def _execute_tasks(self):
        # Continuously check and execute tasks from the task queue
        while True:
            if self.task_queue.get_len() != 0:
                # Pop task from task_queue
                task_info = self.task_queue.pop()
                # Start a new process to handle the output for the task
                process = threading.Thread(target=self.handlers[task_info['handler_name']].handle_task, args=(task_info,))
                process.name = f'{task_info["handler_name"]} execute'
                process.start()   
            time.sleep(0.001)

                
   
if __name__ == '__main__':
    
    GPIO.setmode(GPIO.BCM)
    Control(reset_database=True)

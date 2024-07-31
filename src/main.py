import multiprocessing

from components import *
from handlers import *


class TaskQueue:
    def __init__(self):
        # Use a multiprocessing manager to create a shared list for tasks
        manager = multiprocessing.Manager()
        self.tasks = manager.list()            
        # Create a lock to synchronize access to the task queue
        self.lock = multiprocessing.Lock()
    
    def append(self, task_info):
        # Append a new task to the task queue in a safe manner
        with self.lock:
            self.tasks.append(task_info)
            return True
    
    def pop(self):
        # Pop a task from the task queue in a safe manner
        with self.lock:
            if self.tasks:
                return self.tasks.pop(0)
            return None
        
    def get_len(self):
        # Get the length of the task queue in a safe manner
        with self.lock:
            return len(list(self.tasks))


class Control:
    def __init__(self):
        # Initialize the task queue
        self.task_queue = TaskQueue()
        
        # Initialize handlers and pass the task queue to them
        self.handlers = {
            'battery': BatteryHandler(self.task_queue), 
        }
    
        # Start listening processes for each handler
        self._start_listening()
        
        # Stat a process to execute tasks from the queue 
        process = multiprocessing.Process(target=self._execute_tasks)
        process.start()
        

    def _start_listening(self):
        # Start listening processes for input handlers
        for handler in self.handlers:
            if handler.run_input_thread:
                process = multiprocessing.Process(target=handler.listen)
                process.start()


    def _execute_tasks(self):
        # Continuously check and execute tasks from the task queue
        while True:
            if self.task_queue.get_len() != 0:
                # Pop task from task_queue
                task_info = self.task_queue.pop()
                (requester_name, handler_name, task, task_priority) = task_info          
                
                # Start a new process to handle the output for the task
                process = multiprocessing.Process(target=self.handlers[handler_name].handle_output, args=task_info)
                process.start()             
                
   
if __name__ == '__main__':
    # Initialize the Control class, which starts all processes
    Control()
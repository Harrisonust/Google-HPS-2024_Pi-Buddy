import multiprocessing


from handlers import *
from test_functions import *


class TaskQueue:
    def __init__(self):
        # Use a multiprocessing manager to create a shared list for tasks
        self.tasks = multiprocessing.Queue()
        # Create a lock to synchronize access to the task queue
        self.lock = multiprocessing.Lock()
    
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
    def __init__(self, debug=False, test_function=None):
        # Debug option
        self.debug = debug
        
        # Initialize the task queue
        self.task_queue = TaskQueue()
        
        
        # Initialize handlers and pass the task queue to them
        self.handlers = {
            'battery': BatteryHandler(self.task_queue, debug=self.debug)
        }
    
        # Start listening processes for each handler
        self._start_listening()
        
        # Stat a process to execute tasks from the queue 
        process = multiprocessing.Process(target=self._execute_tasks)
        process.start()
        
        
        if self.debug:
            # Run test_function if self.debug is set to True
            test_process = multiprocessing.Process(target=test_function, args=(self.task_queue,))
            test_process.start()
        

    def _start_listening(self):
        # Start listening processes for input handlers
        for handler_name in self.handlers:
            handler = self.handlers[handler_name]
            if handler.run_input_process:
                process = multiprocessing.Process(target=handler.listen)
                process.start()


    def _execute_tasks(self):
        # Continuously check and execute tasks from the task queue
        while True:
            if self.task_queue.get_len() != 0:
                # Pop task from task_queue
                task_info = self.task_queue.pop()     
                
                # Start a new process to handle the output for the task
                process = multiprocessing.Process(target=self.handlers[task_info['handler_name']].handle_task, args=(task_info,))
                process.start()             
                
   
if __name__ == '__main__':
    # Debug option
    debug = True
    test_function = battery_charge_discharge_test
    
    # Initialize the Control class, which starts all processes
    Control(debug=debug, test_function=test_function)
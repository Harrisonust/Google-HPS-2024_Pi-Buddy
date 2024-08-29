import multiprocessing


from value_manager import ValueManager


class Handler:
    def __init__(self, task_queue):
        self.run_input_process = None       # Required; indicator if this handler listens to input
        self.task_queue = task_queue        # Required; task queue to be assigned
        
        self.component = None               # Required, can have multiple; component driver
        
        self.state = ValueManager(None)     # Optional, can have multiple; indicators of the current status of the component(s) and handler
    
    
    def listen(self):
        # Required if self.run_input_process == True; method to be overriden by subclasses to listen to input
        raise TypeError(f'Invalid call to "listen" function')
    
    
    def handle_task(self):
        # Required if component as output functions; method to handle task from task_queue
        raise TypeError(f'Invalid call to "handle_task" function')
        
import multiprocessing


class  ValueManager:
    def __init__(self, value):
        # Initialize a shared value with a lock for safe access
        self.value = value
        self.lock = multiprocessing.Lock()

    def reveal(self):
        # Return the current value in a safe manner
        with self.lock:
            return self.value
    
    def overwrite(self, value):
        # Overwrite the current value in a safe manner
        with self.lock:
            self.value = value


class Handler:
    def __init__(self):
        self.run_input_process = None       # Required; indicator if this handler listens to input
        self.task_queue = None              # Required; task queue to be assigned
        
        self.component = None               # Required, can have multiple; component driver
        
        self.state = ValueManager(None)     # Optional, can have multiple; indicators of the current status of the component(s) and handler
    
    
    def listen(self):
        # Required if self.run_input_process == True; method to be overriden by subclasses to listen to input
        raise TypeError(f'Invvalid call to "listen" function')
    
    
    def handle_task(self):
        # Required if component as output functions; method to handle task from task_queue
        raise TypeError(f'Invalid call to "handle_task" function')
        
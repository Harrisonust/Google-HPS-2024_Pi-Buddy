import threading

#from value_manager import ValueManager
import sys
import termios
import tty

class TeleopHandler:
    def __init__(self, task_queue):
        self.run_input_process = None       # Required; indicator if this handler listens to input
        self.task_queue = task_queue        # Required; task queue to be assigned
        
        self.task = threading.Thread(target=self.control)
        self.task.start()
   

    def get_key(self):
        """Capture a single key press."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    # Define the commands for each key press
    def control(self):
        while True:
            key = self.get_key()

            if key == 'w':
                self.move_forward()
            elif key == 's':
                self.move_backward()
            elif key == 'a':
                self.turn_left()
            elif key == 'd':
                self.turn_right()
            elif key == ' ':
                self.stop_movement()
            elif key == 'q':
                print("Quitting...")
                break 

    def move_forward(self):
        print("Moving forward")
        self.task_queue.append({
            'requester_name': 'teleop',
            'handler_name':'robot_movement',
            'task': 'UPDATE_MOVEMENT',
            'task_priority': 1,
            'operation': 'move_forward',
        })

    def move_backward(self):
        print("Moving backward")
        self.task_queue.append({
            'requester_name': 'teleop',
            'handler_name':'robot_movement',
            'task': 'UPDATE_MOVEMENT',
            'task_priority': 1,
            'operation': 'move_backward',
        })

    def turn_left(self):
        print("Turning left")
        self.task_queue.append({
            'requester_name': 'teleop',
            'handler_name':'robot_movement',
            'task': 'UPDATE_MOVEMENT',
            'task_priority': 1,
            'operation': 'turn_left',
        })

    def turn_right(self):
        print("Turning right")
        self.task_queue.append({
            'requester_name': 'teleop',
            'handler_name':'robot_movement',
            'task': 'UPDATE_MOVEMENT',
            'task_priority': 1,
            'operation': 'turn_right',
        })

    def stop_movement(self):
        print("Stopping movement")
        self.task_queue.append({
            'requester_name': 'teleop',
            'handler_name':'robot_movement',
            'task': 'UPDATE_MOVEMENT',
            'task_priority': 1,
            'operation': 'stop_movement',
        })

    
    def listen(self):
        # Required if self.run_input_process == True; method to be overriden by subclasses to listen to input
        raise TypeError(f'Invvalid call to "listen" function')
    
    
    def handle_task(self):
        # Required if component as output functions; method to handle task from task_queue
        raise TypeError(f'Invalid call to "handle_task" function')
        
if __name__ == '__main__':
    handler = TeleopHandler()


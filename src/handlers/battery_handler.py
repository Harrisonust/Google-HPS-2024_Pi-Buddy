import time


from components.pisugar3 import Battery
from handlers import Handler, ValueManager


class BatteryHandler(Handler):
    
    READ_PERIOD = 10        # Define the period to read battery power
    LOW_POWER = 25          # Define the low power threshold
    FULL_POWER = 99         # Define the full power threshold
    
    
    def __init__(self, task_queue):
        self.run_input_process = True   # Indicate that this handler listens to input
        self.task_queue = task_queue
        
        self.battery = Battery()        # The battery component
        
        # States to describe the current status of the battery and battery handler
        self.battery_busy = ValueManager(False)
        self.battery_output_state = ValueManager('IDLE')
        self.battery_power_state = ValueManager('NORMAL')
    
    
    def listen(self):
        # Continuously listen to battery power level
        while True:
            battery_power = self.battery.get_battery()
            self._handle_input(battery_power)
            
            # Wait for a defined period before checking again
            time.sleep(self.__class__.READ_PERIOD)
    
    
    def _handle_input(self, battery_power):
        # Handle battery power input and update battery_power_state accordingly
        current_battery_power_state = self.battery_power_state.reveal()
        
        # Battery goes to low power state
        if battery_power <= self.__class__.LOW_POWER\
            and current_battery_power_state != 'LOW_POWER':
                self.battery_power_state.overwrite('LOW_POWER')
                self.task_queue.append(('screen', 'HUNGRY', 1))

        # Battery goes to full power state
        elif battery_power >= self.__class__.FULL_POWER\
            and current_battery_power_state != 'FULL_POWER':
                self.battery_power_state.overwrite('FULL_POWER')
                self.task_queue.append(('screen', 'ENERGETIC', 1))
        
        # Battery goes to normal power state
        elif battery_power >= self.__class__.LOW_POWER\
            and battery_power <= self.__class__.FULL_POWER\
            and current_battery_power_state != 'NORMAL_POWER':
                self.battery_power_state.overwrite('NORMAL_POWER')

    
    def handle_task(self, task_info):
        # Handle output tasks for the battery
        (requester_name, handler_name, task, task_priority) = task_info
        
        # If battery is busy, pend task
        if self.battery_busy.reveal():
            self.task_queue.append(task_info)
        
        else:
            # Set battery to busy
            self.battery_busy.overwrite(True)
            current_battery_output_state = self.battery_output_state.reveal()
            
            # Execute tasks
            if task == 'RESUME_CHARGING':
                if current_battery_output_state == 'IDLE':
                    self.battery.resume_charging()
                    self.battery_output_state.overwrite('CHARGING')
                
            elif task == 'STOP_CHARGING':
                if current_battery_output_state == 'CHARGING':
                    self.battery.stop_charging()
                    self.battery_output_state.overwrite('IDLE')
            
            else:
                raise ValueError(f"Invalid task {task} handled to {handler_name} requested by {requester_name}")
            
            # Set battery to not busy
            self.battery_busy.overwrite(False)
import time
from enum import Enum

from components.pisugar3.pisugar3 import BatteryManager
# from test_components.battery import TestBattery
from handlers.handler import Handler
from value_manager import ValueManager

'''
BatteryManager functions utilized:
    * set_battery_charging(): lines 75 & 80
    * get_battery_percentage(): line 41
    * get_battery_charging(): line 42
'''


class BatteryOutputState(Enum):
    IDLE = 0 
    CHARGING = 1
    

class BatteryHandler(Handler):   
    def __init__(self, task_queue, debug=False):
        self.debug = debug
        
        self.run_input_process = True   # Indicate that this handler listens to input
        self.task_queue = task_queue
        
        self.battery = BatteryManager()

        self.battery_busy = ValueManager(int(False))
        
        # Set as class variables because they may be of use in the future (?) 
        self.battery_level = ValueManager(0)
        self.battery_charging = ValueManager()
        
    
    def listen(self):
        # Continuously listen to battery power level
        while True:
            self.battery_level.overwrite(self.battery.get_battery_percentage())
            self.battery_charging.overwrite(self.battery.get_battery_charging())
            
            # Write task to menu_screen to update battery level and charging statuses
            self.task_queue.append({
                'requester_name': 'battery',
                'handler_name': 'menu_screen',
                'task': 'UPDATE_BATTERY_STATE',
                'task_priority': 1,
                'battery_level': self.battery_level,
                'battery_charging': self.battery_charging        
            })
            
            # Wait for a defined period before checking again
            time.sleep(5)
    
    
    def handle_task(self, task_info):
        # Handle output tasks for the battery
        
        # If battery is busy, pend task
        if self.battery_busy.reveal():
            self.task_queue.append(task_info)
        
        else:
            # Set battery to busy
            self.battery_busy.overwrite(int(True))
            
            # Get current battery states
            current_battery_output_state = self.battery_output_state.reveal()
            
            ### FOR FUTURE USB HUB ###
            if task_info['task'] == 'RESUME_CHARGING':
                if current_battery_output_state == BatteryOutputState.IDLE:
                    self.battery.set_battery_charging(on_off=True)
                    self.battery_output_state.overwrite(BatteryOutputState.CHARGING)
                
            elif task_info['task'] == 'STOP_CHARGING':
                if current_battery_output_state == BatteryOutputState.CHARGING:
                    self.battery.set_battery_charging(on_off=False)
                    self.battery_output_state.overwrite(BatteryOutputState.IDLE)  
            else:
                raise ValueError(f"Invalid task {task_info}")
            ############################
            
            # Set battery to not busy
            self.battery_busy.overwrite(int(False))
import time
from enum import Enum

from components.pisugar3.pisugar3 import BatteryManager
# from test_components.battery import TestBattery
from handlers.handler import Handler
from value_manager import ValueManager


class BatteryConfig(Enum):
    READ_PERIOD = 1         # Define the period to read battery power
    LOW_POWER = 25          # Define the low power threshold
    FULL_POWER = 99         # Define the full power threshold


class BatteryOutputState(Enum):
    IDLE = 0 
    CHARGING = 1
    

class BatteryPowerState(Enum):
    NORMAL_POWER = 0
    LOW_POWER = 1
    FULL_POWER = 2


class BatteryHandler(Handler):   
    def __init__(self, task_queue, debug=False):
        self.debug = debug
        
        self.run_input_process = True   # Indicate that this handler listens to input
        self.task_queue = task_queue
        
        self.battery = BatteryManager()
        # self.battery = TestBattery() if self.debug else Battery()   # The battery component
        
        # States to describe the current status of the battery and battery handler
        self.battery_busy = ValueManager(int(False))
        self.battery_output_state = ValueManager(BatteryOutputState.IDLE, enum=BatteryOutputState)
        self.battery_power_state = ValueManager(BatteryPowerState.NORMAL_POWER, enum=BatteryPowerState)
    
    
    def listen(self):
        # Continuously listen to battery power level
        while True:
            battery_power = self.battery.get_battery_percentage()
            self._handle_input(battery_power)
            
            # Wait for a defined period before checking again
            time.sleep(BatteryConfig.READ_PERIOD.value)
    
    
    def _handle_input(self, battery_power):

        # Handle battery power input and update battery_power_state accordingly
        current_battery_power_state = self.battery_power_state.reveal()
        
        self.task_queue.append({
            'reqeuster_name': 'battery',
            'handler_name': 'menu_screen',
            'task': 'BATTERY_POWER_UPDATE',
            'args': battery_power,
            'task_priority': 1
        })

        # Battery goes to low power state
        if battery_power <= BatteryConfig.LOW_POWER.value\
            and current_battery_power_state != BatteryPowerState.LOW_POWER:
                self.battery_power_state.overwrite(BatteryPowerState.LOW_POWER)
                

        # Battery goes to full power state
        elif battery_power >= BatteryConfig.FULL_POWER.value\
            and current_battery_power_state != BatteryPowerState.FULL_POWER:
                self.battery_power_state.overwrite(BatteryPowerState.FULL_POWER)
        
        # Battery goes to normal power state
        elif battery_power >= BatteryConfig.LOW_POWER.value\
            and battery_power <= BatteryConfig.FULL_POWER.value\
            and current_battery_power_state != BatteryPowerState.NORMAL_POWER:
                self.battery_power_state.overwrite(BatteryPowerState.NORMAL_POWER)

    
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
            
            # Execute tasks
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
    
            
            # Set battery to not busy
            self.battery_busy.overwrite(int(False))
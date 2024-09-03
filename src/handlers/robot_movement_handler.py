import threading
import time

from value_manager import ValueManager
from components.ir import IR
from pin_defines import *
from components.vl53l1x.vl53l1x import VL53L1X
from components.tb6612fng import DualChannelMotor

class RobotMovementHandler:
    def __init__(self, task_queue):
        self.run_input_process = True       # Required; indicator if this handler listens to input
        self.task_queue = task_queue              # Required; task queue to be assigned

        self.robot_movement_busy = ValueManager(0)
        self.robot_base = DualChannelMotor(23, 24, 25, 1, 12, 16, pin_standby=None)
        self.state = 'Teleop'

        self.tof_distance = None
        self.ir_is_triggered = None

        ir_task_handle = threading.Thread(target=self.ir_task)
        tof_task_handle = threading.Thread(target=self.tof_task)
        ir_task_handle.start()
        tof_task_handle.start()

        self.robot_base_speed = 10

    def listen(self):
        while 1:
            #print(f"robot movement -- IR:{self.ir_is_triggered} TOF:{self.tof_distance}")
            if self.ir_is_triggered or (self.tof_distance != None and self.tof_distance < 50): 
                self.robot_base.stop()
                self.robot_base.move(-50)
                self.robot_base.rotate(180)
                time.sleep(0.1)
            else:
                if self.state == 'Teleop':
                    pass
                elif self.state == 'Curious':
                    self.robot_base.random_walk()
                elif self.state == 'Scared':
                    self.robot_base.move(-50) # 50 mm
                elif self.state == 'Call_and_come':
                    pass
            time.sleep(0.1)

    def ir_task(self):
        self.ir = IR(PIN_IR)

        while 1:
            self.ir_is_triggered = self.ir.is_triggered()
            time.sleep(0.1)

    def tof_task(self):
        self.tof = VL53L1X()
        self.tof.init_sensor()
        self.tof.start_continuous(period_ms=50)
        while 1:
            self.tof_distance = self.tof.get_distance()
            time.sleep(0.1)

        self.tof.stop_continuous()
        self.tof.close()
    
    def handle_task(self, task_info):
        if self.robot_movement_busy.reveal():
            self.task_queue.append(task_info)

        else:
            self.robot_movement_busy.overwrite(True)
            if task_info['handler_name'] == 'robot_movement':
                self.robot_base.set_speed(40)
                if task_info['operation'] == 'move_forward':
                    print('in robot movement handler move forward')
                    self.robot_base.move(0)
                elif task_info['operation'] == 'move_backward':
                    print('in robot movement handler move backward')
                    self.robot_base.move(1)
                elif task_info['operation'] == 'turn_left':
                    print('in robot movement handler turn left')
                    self.robot_base.rotate(0)
                elif task_info['operation'] == 'turn_right':
                    print('in robot movement handler turn right')
                    self.robot_base.rotate(1)
                elif task_info['operation'] == 'stop_movement':
                    print('in robot movement handler stop movement')
                    self.robot_base.stop()

            self.robot_movement_busy.overwrite(False)

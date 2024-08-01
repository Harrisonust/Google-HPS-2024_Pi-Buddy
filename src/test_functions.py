import time


def battery_charge_discharge_test(task_queue):
    
    charge = {
        'requester_name': 'battery_charge_discharge_test',
        'handler_name': 'battery',
        'task': 'RESUME_CHARGING',
        'task_priority': None
    }
    discharge = {
        'requester_name': 'battery_charge_discharge_test',
        'handler_name': 'battery',
        'task': 'STOP_CHARGING',
        'task_priority': None
    }
    
    time.sleep(15)
    task_queue.append(charge)
    alert_task_append('BatteryTester', charge)
    
    time.sleep(15)
    task_queue.append(discharge)
    alert_task_append('BatteryTester', discharge)
    

def alert_task_append(requester, task_info):
    print(f'{requester}:\t task appended')
    print(f'\t\t task_info                    = {task_info}')
    print(f'')
    
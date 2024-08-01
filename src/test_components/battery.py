from value_manager import ValueManager


class TestBattery:
    def __init__(self):
        self.power = 50
        self.change_per_call = ValueManager(-5)
    
    def get_battery(self):
        self.power += self.change_per_call.reveal()
        self.power = min(100, max(0, self.power))
        print(f'TestBattery:\t get_battery was called, power = {self.power}, self.change_per_call = {self.change_per_call.reveal()}')
        return self.power
    
    def resume_charging(self):
        self.change_per_call.overwrite(10)
        print(f'TestBattery:\t resume_charging was called, self.change_per_call = {self.change_per_call.reveal()}')
    
    def stop_charging(self):
        self.change_per_call.overwrite(-5)
        print(f'TestBattery:\t stop_charging was called, self.change_per_call = {self.change_per_call.reveal()}')
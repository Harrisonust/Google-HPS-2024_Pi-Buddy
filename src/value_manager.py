import multiprocessing


class  ValueManager:
    def __init__(self, value, enum=None):
        # For integer values
        if enum == None:
            self.enum_flag = False
            self.enum = None
            self.value = multiprocessing.Value('i', value)
            self.lock = multiprocessing.Lock()
        
        # For enum values
        else:
            self.enum_flag = True
            self.enum = enum
            self.value = multiprocessing.Value('i', value.value)
            self.lock = multiprocessing.Lock()


    def reveal(self):
        # Return the current value in a safe manner
        with self.lock:
            if self.enum_flag:
                return self.enum(self.value.value)
            return self.value.value
        
    
    def overwrite(self, value):
        # Overwrite the current value in a safe manner
        with self.lock:
            if self.enum_flag:
                self.value.value = value.value
                return
            self.value.value = value
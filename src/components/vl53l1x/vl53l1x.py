import time
from  smbus2 import SMBus, i2c_msg

class VL53L1X:
    def __init__(self):
        self.bus = SMBus(1)
        self.address = 0x29

    def write_register(self, register, value:int, wlen=1):
        wbuf = [register>>8, register&0xFF]
        for i in range(wlen-1, -1, -1):
            wbuf.append(value >> (8*i))
        write = i2c_msg.write(self.address, wbuf)
        self.bus.i2c_rdwr(write)

    def read_register(self, register, rlen=1):
        write = i2c_msg.write(self.address, [register>>8, register&0xFF])
        self.bus.i2c_rdwr(write)
        read = i2c_msg.read(self.address, rlen)
        self.bus.i2c_rdwr(read)
        if rlen == 1:
            return int.from_bytes(read)
        else:
            return read

    def init_sensor(self):
        self.write_register(0x0000, 0x00, wlen=1)
        time.sleep(0.1)
        self.write_register(0x0000, 0x01, wlen=1) # reset
        time.sleep(1)
        
        self.fast_osc_freq = int.from_bytes(self.read_register(0x0006, rlen=2))
        self.osc_calibrate_val = int.from_bytes(self.read_register(0x00DE, rlen=2))

    def start_continuous(self, period_ms):
        self.write_register(0x006C, self.osc_calibrate_val, 4)
        self.write_register(0x0086, 0x01, wlen=1) # system interrupt clear
        self.write_register(0x0087, 0x40, wlen=1) # continuous

    def get_model_id(self):
        return self.read_register(0x010F, 1)

    def start_ranging(self):
        self.write_register(0x0000, 0x01, wlen=1)  # Example command to start ranging

    def check_data_ready(self):
        status = self.read_register(0x0031, 1)  # Example register for status
        return (status & 0x01) == 0x00

    def get_distance(self):
        if self.check_data_ready():
            rbuf = list(self.read_register(0x0089, 17))  # Example register for distance
            # 0: range status
            # 1: report status (not used)
            # 2: stream count
            # 3: dss actual effective spads sd0 (high)
            # 4: dss actual effective spads sd0 (low)
            # 5: peak signal count rate mcps sd0 (not used)
            # 6: peak signal count rate mcps sd0
            # 7: ambient count rate mcps sd0 (high)
            # 8: ambient count rate mcps sd0 (low)
            # 9:  sigma sd0 (not used)
            # 10: sigma sd0 (not used)
            # 11: phase sd0 (not used)
            # 12: phase sd0 (not used)
            # 13: final crosstalk corrected range mm sd0 (high) 
            # 14: final crosstalk corrected range mm sd0 (low)
            # 15: peak signal count rate crosstalk corrected mcps sd0 (high)
            # 16: peak signal count rate crosstalk corrected mcps sd0 (low)
            distance = (rbuf[13] << 8 | rbuf[14])
            return distance
        else:
            return None

    def stop_ranging(self):
        self.write_register(0x0000, 0x00)  # Example command to stop ranging

    def close(self):
        self.bus.close()


if __name__ == "__main__":
    sensor = VL53L1X()

    try:
        sensor.init_sensor()
        print(f'0x{sensor.get_model_id():02X}')

        sensor.start_continuous(50)
        
        while True:
            distance = sensor.get_distance()
            #if distance is not None:
            print(f"Distance: {distance} mm")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping ranging...")
    finally:
        sensor.stop_ranging()
        sensor.close()


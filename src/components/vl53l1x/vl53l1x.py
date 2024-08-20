import time
from  smbus2 import SMBus, i2c_msg
from vl53l1x_reg import *

class VL53L1X:
    def __init__(self):
        self.bus = SMBus(1)
        self.address = 0x29

    def _write_register(self, register, value, wlen=1):
        wbuf = [register>>8, register&0xFF]
        for i in range(wlen-1, -1, -1):
            wbuf.append((value >> (8*i)) & 0xFF)
        write = i2c_msg.write(self.address, wbuf)
        self.bus.i2c_rdwr(write)

    def _read_register(self, register, rlen=1):
        write = i2c_msg.write(self.address, [register>>8, register&0xFF])
        self.bus.i2c_rdwr(write)
        read = i2c_msg.read(self.address, rlen)
        self.bus.i2c_rdwr(read)
        if rlen == 1:
            return int.from_bytes(read)
        else:
            return read

    def get_model_id(self):
        return self._read_register(IDENTIFICATION_MODEL_ID, rlen=1)

    def init_sensor(self):
        self._write_register(SOFT_RESET, 0x00, wlen=1)
        time.sleep(0.1)
        self._write_register(SOFT_RESET, 0x01, wlen=1) # reset
        time.sleep(1)
        
        self.fast_osc_freq = int.from_bytes(self._read_register(MEASURED_FAST_OSC_FREQ, rlen=2))
        self.osc_calibrate_val = int.from_bytes(self._read_register(OSC_CALIBRATE_VAL, rlen=2))
        
        # set distance mode 
        self.set_distance_mode(2)

        # set measurement timing budget

    
    def set_distance_mode(self, mode):
        if mode == 0: # short
            self._write_register(VCSEL_PERIOD_A,    0x07, wlen=1)
            self._write_register(VCSEL_PERIOD_B,    0x05, wlen=1)
            self._write_register(VALID_PHASE_HIGH,  0x38, wlen=1)
            self._write_register(WOI_SD0,           0x07, wlen=1)
            self._write_register(WOI_SD1,           0x05, wlen=1)
            self._write_register(INITIAL_PHASE_SD0, 6,    wlen=1)
            self._write_register(INITIAL_PHASE_SD1, 6,    wlen=1)
        elif mode == 1: # medium
            self._write_register(VCSEL_PERIOD_A,    0x0B, wlen=1)
            self._write_register(VCSEL_PERIOD_B,    0x09, wlen=1)
            self._write_register(VALID_PHASE_HIGH,  0x78, wlen=1)
            self._write_register(WOI_SD0,           0x0B, wlen=1)
            self._write_register(WOI_SD1,           0x09, wlen=1)
            self._write_register(INITIAL_PHASE_SD0, 10,   wlen=1)
            self._write_register(INITIAL_PHASE_SD1, 10,   wlen=1)
        elif mode == 2: # long
            self._write_register(VCSEL_PERIOD_A,    0x0F, wlen=1)
            self._write_register(VCSEL_PERIOD_B,    0x0D, wlen=1)
            self._write_register(VALID_PHASE_HIGH,  0xB8, wlen=1)
            self._write_register(WOI_SD0,           0x0F, wlen=1)
            self._write_register(WOI_SD1,           0x0D, wlen=1)
            self._write_register(INITIAL_PHASE_SD0, 14,   wlen=1)
            self._write_register(INITIAL_PHASE_SD1, 14,   wlen=1)

    def start_continuous(self, period_ms):
        self._write_register(INTER_MEASUREMENT_PERIOD, self.osc_calibrate_val * period_ms, wlen=4) # set inter-measurement period in miiliseconds
        self._write_register(INTERRUPT_CLEAR, 0x01, wlen=1) # system interrupt clear
        self._write_register(MODE_START, 0x40, wlen=1) # continuous

    def stop_continuous(self):
        self._write_register(MODE_START, 0x80, wlen=1)

    def start_ranging(self):
        self._write_register(SOFT_RESET, 0x01, wlen=1)  

    def stop_ranging(self):
        self._write_register(SOFT_RESET, 0x00, wlen=1)  # Example command to stop ranging

    def check_data_ready(self):
        status = self._read_register(TIO_HV_STATUS, rlen=1)  
        return (status & 0x01) == 0x00

    def get_distance(self):
        if self.check_data_ready():
            rbuf = list(self._read_register(RANGE_STATUS, rlen=17))  
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
            distance = (distance * 2011 + 0x0400) / 0x0800
            return distance
        else:
            return None

    def get_distance_single(self):
        self._write_register(INTERRUPT_CLEAR, 0x01, wlen=1)
        self._write_register(MODE_START, 0x10, wlen=1)
        return self.get_distance()

    def close(self):
        self.bus.close()

if __name__ == "__main__":
    sensor = VL53L1X()

    sensor.init_sensor()
    print(f'0x{sensor.get_model_id():02X}')

    sensor.start_continuous(period_ms=50)
       
    while True:
        distance = sensor.get_distance()
        if distance is not None:
            print(f"Distance: {distance:.2f} mm")
            time.sleep(0.1)
    
    sensor.stop_continuous()
    sensor.close()


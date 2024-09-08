import time
from datetime import datetime
import RPi.GPIO as GPIO
from smbus2 import SMBus
from .pisugar3_reg import *

class BatteryManager: 
	def __init__(self):
		self._i2c = SMBus(1) # /dev/i2c-1
		self._address = PISUGAR3_ADDR
		self.set_rtc()

	def _write_byte(self, reg, value) -> None:
		self._i2c.write_byte_data(self._address, reg, value)

	def _read_byte(self, reg) -> int:
		return self._i2c.read_byte_data(self._address, reg)

	def _read_bits(self, reg, bit, len=1) -> int:
		val = self._read_byte(reg)
		return (val >> bit) & (0x1 << len) - 1

	def _disable_write_protection(self) -> None:
		self._write_byte(WRITE_PROTECTION, 0x29)

	def _enable_write_protection(self) -> None:
		self._write_byte(WRITE_PROTECTION, 0xFF)

	def _get_write_protection(self) -> int:
		return self._read_byte(WRITE_PROTECTION)

	def _get_status1(self) -> int:
		return self._read_byte(STATUS1)

	def _get_status2(self) -> int:
		return self._read_byte(STATUS2)

	####################### USER #############################

	def get_external_power_to_battery(self) -> bool:
		# read only 
		# return true if a power cable is connected to pisugar
		return self._read_bits(STATUS1, POWER_SUPPLY_BIT, POWER_SUPPLY_LEN)

	def set_battery_charging(self, on_off) -> None:
	 	# if on:  enable battery charging
		# if off: disable battery charging
		status1 = self._get_status1()
		if on_off == 1:
			status1 |= (1 << CHARGING_SWITCH_BIT)
		elif on_off == 0:
			status1 &= ~(1 << CHARGING_SWITCH_BIT)
		self._disable_write_protection()
		self._write_byte(STATUS1, status1)
		self._enable_write_protection()

	def get_battery_charging(self) -> bool:
		# read, return if battery charging is allowed
		return self._read_bits(STATUS1, CHARGING_SWITCH_BIT, CHARGING_SWITCH_LEN)
	
	def set_battery_output(self, on_off) -> None:
		# if on:  enable battery output to rpi
		# if off: disable battery output to rpi
		status1 = self._get_status1()
		if on_off == 1:
			status1 |= (1 << OUTPUT_SWITCH_BIT)
		elif on_off == 0:
			status1 &= ~(1 << OUTPUT_SWITCH_BIT)
		self._disable_write_protection()
		self._write_byte(STATUS1, status1)
		self._enable_write_protection()

	def get_battery_output(self) -> bool:
		return self._read_bits(STATUS1, OUTPUT_SWITCH_BIT, OUTPUT_SWITCH_LEN)

	def set_charging_protection(self, on_off):
		reg_value = self._read_byte(CHARGING_PROTECTION)
		if on_off == 0:
			reg_value &= ~(1 << CHARGING_PROTECTION_BIT)
		elif on_off == 1:
			reg_value |= (1 << CHARGING_PROTECTION_BIT)
		self._disable_write_protection()
		self._write_byte(CHARGING_PROTECTION, reg_value)
		self._enable_write_protection()

	def get_charging_protection(self) -> bool:
		return self._read_bits(CHARGING_PROTECTION, CHARGING_PROTECTION_BIT, CHARGING_PROTECTION_LEN)

	def get_voltage(self) -> float:
		high = self._read_byte(VOLTAGE_HIGH)
		low  = self._read_byte(VOLTAGE_LOW)
		return (high << 8 | low) / 1000

	def get_battery_percentage(self) -> int: 
		return self._read_byte(POWER_PROPORTION)
	
	def get_custom_button_status(self) -> bool:
		return self._read_bits(CUSTOM_BTN, CUSTOM_BTN_BIT, CUSTOM_BTN_LEN)

	def get_rtc(self):
		year 	= self._read_byte(RTC_YEAR) + 2000
		month 	= self._read_byte(RTC_MONTH)
		day 	= self._read_byte(RTC_DAY)
		weekday = self._read_byte(RTC_WEEKDAY)
		hour 	= self._read_byte(RTC_HOUR)
		minute 	= self._read_byte(RTC_MINUTE)
		second 	= self._read_byte(RTC_SECOND)
		return f"{year}/{month}/{day}({weekday+1}) {hour}:{minute}:{second}"

	def set_rtc(self) -> None:
		now = datetime.now()
		year 	= now.year - 2000
		month 	= now.month
		day 	= now.day
		weekday = now.weekday()
		hour 	= now.hour
		minute 	= now.minute
		second 	= now.second
		print(f"{year}/{month}/{day}({weekday+1}) {hour}:{minute}:{second}")

		self._disable_write_protection()
		self._write_byte(RTC_YEAR, year)
		self._write_byte(RTC_MONTH, month)
		self._write_byte(RTC_DAY, day)
		self._write_byte(RTC_WEEKDAY, weekday)
		self._write_byte(RTC_HOUR, hour)
		self._write_byte(RTC_MINUTE, minute)
		self._write_byte(RTC_SECOND, second)
		self._enable_write_protection()

	def get_chip_temp(self) -> int:
		return self._read_byte(CHIP_TEMP) - 40

	def __del__(self):
		self._i2c.close()

if __name__ == '__main__':
	GPIO.setmode(GPIO.BCM)
	battery_manager = BatteryManager()
	battery_manager.set_battery_charging(1)
	battery_manager.set_battery_output(1)
	while 1:
		print("external power exist: ", battery_manager.get_external_power_to_battery())
		print("enable battery charging: ", battery_manager.get_battery_charging())
		print("enable battery to rpi: ", battery_manager.get_battery_output())
		print("enable charging protection: ", battery_manager.get_charging_protection())
		print(f"battery voltage: {battery_manager.get_voltage()} V")
		print(f"battery level: {battery_manager.get_battery_percentage()} %")
		print(f"chip temperature: {battery_manager.get_chip_temp()} C")
		print(f"current time: {battery_manager.get_rtc()}")
		print()
		time.sleep(1)
	

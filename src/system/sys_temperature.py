def get_rpi_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = int(f.read()) / 1000.0
    return temp

temperature = get_rpi_temperature()
print(f"Raspberry Pi Temperature: {temperature:.2f}°C")


# Desktop Assistant Pet (DAP)

## Hardware

### Pin definitions
|Connection|BCM|Physical|Physical|BCM|Connection|
|---|---|---|---|---|---|
|X|3.3V|1|2|5V|X|
|I2C SDA|GPIO 2|3|4|5V|X|
|I2C SCL|GPIO 3|5|6|G|X|
|Motor ENC1A|GPIO 4|7|8|GPIO 14|LCD DC|
|X|G|9|10|GPIO 15|LCD RST|
|Motor ENC1B|GPIO 17|11|12|GPIO 18|I2S CLK|
|Motor ENC2A|GPIO 27|13|14|G|X|
|Motor ENC2B|GPIO 22|15|16|GPIO 23|Motor PWMA|
|X|3.3V|17|18|GPIO 24|Motor INA1|
|SPI MOSI/LCD DIN|GPIO 10|19|20|G|X|
|SPI MISO|GPIO 9|21|22|GPIO 25|Motor INA2|
|SPI SCLK/LCD SCK|GPIO 11|23|24|GPIO 8|Reserved by SPI|
|X|G|25|26|GPIO 7|Reserved by SPI|
|Menu ENC1A|GPIO 0|27|28|GPIO 1|Motor PWMB|
|Menu ENC1B|GPIO 5|29|30|G|X|
|Menu ENC2A|GPIO 6|31|32|GPIO 12|Motor INB1|
|Menu ENC2B|GPIO 13|33|34|G|X|
|I2S WS|GPIO 19|35|36|GPIO 16|Motor INB2|
|IR|GPIO 26|37|38|GPIO 20|I2S DIN|
|X|G|39|40|GPIO 21|I2S DOUT|

To be added: motor standby pin

## Installation
```sh
./install.sh
```



# Desktop Assistant Pet (DAP)

## Hardware
### Pin definitions
|Connection|BCM|BCM|Connection|
|---|---|---|---|
|X|3.3V|5V|X|
|I2C SDA|2|5V|X|
|I2C SCL|3|G|X|
|Motor ENC1A|4|14|IR|
|X|G|15|Reserve|
|Motor ENC1B|17|18|I2S CLK|
|Motor ENC2A|27|G|X|
|Motor ENC2B|22|23|Motor PWMA|
|X|3.3V|24|Motor INA1|
|SPI MOSI|10|G|X|
|SPI MISO|9|25|Motor INA2|
|SPI SCLK|11|8|Reserve|
|X|G|7|Reserve|
|Menu ENC1A|0|1|Motor PWMB|
|Menu ENC1B|5|G|X|
|Menu ENC2A|6|12|Motor INB1|
|Menu ENC2B|13|G|X|
|I2S WS|19|16|Motor INB2|
|Motor Standby|26|20|I2S DIN|
|X|G|21|I2S DOUT|

## Installation
```sh
./install.sh
```



# CPS

_by [CaptainException](https://github.com/CaptainException) and [MeroFuruya](https://github.com/MeroFuruya)_


A small school project to create a system that might be able to be used as an building access control system.
It is intended to be used with a Raspberry Pi Pico.

## Parts

- Raspberry Pi Pico
- RFID-RC522
- 16x2 LCD Display (I2C) - we used a 1602A
- buzzer with pwm control
- rgb led

## Pinout

#### RFID

| Signal | GPIO | Pin |
| ------ | ---- | --- |
| sck    | GP18 | 24  |
| mosi   | GP19 | 25  |
| miso   | GP16 | 21  |
| rst    | GP17 | 22  |
| sda/cs | GP20 | 26  |

#### Buzzer

| Signal | GPIO | Pin |
| ------ | ---- | --- |
| TTL    | GP0  | 1   |

#### RGB-LED

| Signal | GPIO | Pin |
| ------ | ---- | --- |
| red    | GP1  | 2   |
| green  | GP2  | 3   |
| blue   | GP3  | 5   |

#### LCD Display

| Signal | GPIO | Pin |
| ------ | ---- | --- |
| scl    | GP5  | 7   |
| sda    | GP4  | 6   |

## Libraries

### MFRC522 (RFID)

stolen from: https://github.com/danjperron/micropython-mfrc522

### I2C_LCD

stolen from: https://github.com/brainelectronics/micropython-i2c-lcd

## 
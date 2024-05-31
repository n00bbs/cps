from machine import I2C, Pin
from lcd_i2c import LCD as LcdDriver

class LCD:
  SCREEN_I2C_ADDR = 0x27     # DEC 39, HEX 0x27
  SCREEN_I2C_NUM_ROWS = 2
  SCREEN_I2C_NUM_COLS = 16
  
  def __init__(self, scl: int, sda: int):
    self.i2c = I2C(0, scl=Pin(scl), sda=Pin(sda), freq=800000)
    self.lcd = LcdDriver(
      i2c=self.i2c,
      addr=self.SCREEN_I2C_ADDR,
      cols=self.SCREEN_I2C_NUM_COLS,
      rows=self.SCREEN_I2C_NUM_ROWS
    )
    self.lcd.begin()

  def write(self, text: str):
    self.lcd.clear()
    lines = text.split("\n")
    for i, line in enumerate(lines):
      self.lcd.set_cursor(0, i)
      self.lcd.print(line)
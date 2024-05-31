from machine import I2C, Pin
from lcd import LCD
from rfid import RFID
from status_led import StatusLed
from buzzer import Buzzer
from app import App
import asyncio

current_mode = "read"

lcd = LCD(scl=5, sda=4)
status_led = StatusLed(red=1, green=2, blue=3)
buzzer = Buzzer(pin=0)
rfid = RFID(sck=18, mosi=19, miso=16, rst=17, cs=20)

app = App(lcd, status_led, rfid, buzzer, current_mode)

async def main():
  loop = asyncio.get_event_loop()
  loop.create_task(app.main_loop())
  loop.run_forever()

asyncio.run(main())

from lcd import LCD
from rfid import RFID
from status_led import StatusLed
from noise_hummer import NoiseHummer
from app import App
import asyncio
from util import run_task_factory

current_mode = "read"

lcd = LCD()
status_led = StatusLed()
rfid = RFID()
noise_hummer = NoiseHummer()

app = App(lcd, status_led, rfid, noise_hummer, current_mode)

async def main():
  loop = asyncio.get_event_loop()
  loop.create_task(app.main_loop())
  loop.run_forever()

asyncio.run(main())

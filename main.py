from lcd import LCD
from rfid import RFID
from status_led import StatusLed
import asyncio
from util import run_task_factory

current_mode = "read"

rfid = RFID()
lcd = LCD()
status_led = StatusLed()

status_led_task = None
async def set_status_led_for_time(color: str, time: int | None = None):
  status_led.set_color(color)
  if time is not None:
    await asyncio.sleep(time)
    status_led.off()

set_status_led = run_task_factory(set_status_led_for_time)
'''`Callable[[str, int | None], None]'''

def rfid_on_data_read_start(uid: str):
  print("Data read start for UID: %s" % uid)
  set_status_led("00ff00")
rfid.on_data_read_start = rfid_on_data_read_start

def rfid_on_data_read_end(data: str):
  print("Data read end: %s" % data)
  set_status_led("0000ff", 5)
rfid.on_data_read_end = rfid_on_data_read_end

def rfid_on_data_read_error(error: str):
  print("Data read error: %s" % error)
  set_status_led("ff0000", 5)
rfid.on_data_read_error = rfid_on_data_read_error


# setup RFID
async def print_mode():
  if (current_mode == "read"):
    lcd.write("Mode: Read")
  elif (current_mode == "write"):
    lcd.write("Mode: Write")

asyncio.create_task(print_mode())

async def rfid_loop():
  async def print_mode_after_5():
    await asyncio.sleep(5)
    await print_mode()
  get_print_mode_task = run_task_factory(print_mode_after_5)

  while True:
    if(current_mode == "read"):
      data = rfid.read()
      if data is not None:
        lcd.write(data)
        print("Data: %s" % data)
    elif(current_mode == "write"):
      data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent."
      data_written = rfid.write(data)
      if data_written is not None:
        print("Data written")
        lcd.write("Data written")
        get_print_mode_task()
    await asyncio.sleep(0)

async def main():
  loop = asyncio.get_event_loop()
  loop.create_task(rfid_loop())
  loop.run_forever()

asyncio.run(main())

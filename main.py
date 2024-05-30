from lcd import LCD
from rfid import RFID
import asyncio

current_mode = "write"

rfid = RFID()
lcd = LCD()

async def print_mode():
  if (current_mode == "read"):
    lcd.write("Mode: Read")
  elif (current_mode == "write"):
    lcd.write("Mode: Write")

asyncio.create_task(print_mode())

async def rfid_loop():
  print_mode_task = None
  async def print_mode_after_5():
    await asyncio.sleep(5)
    await print_mode()
  def get_print_mode_task():
    if(print_mode_task is not None):
      print_mode_task.cancel()
    return asyncio.create_task(print_mode_after_5())

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
        print_mode_task = get_print_mode_task()
    await asyncio.sleep(0)

async def main():
  loop = asyncio.get_event_loop()
  loop.create_task(rfid_loop())
  loop.run_forever()

asyncio.run(main())

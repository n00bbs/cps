from lcd import LCD
from rfid import RFID
from status_led import StatusLed
from buzzer import Buzzer
from acces_control import AccessControl
import asyncio
from util import run_task_factory

class App:
  def __init__(self, lcd: LCD, status_led: StatusLed, rfid: RFID, noise_hummer: Buzzer, current_mode: str = "read"):
    self.lcd = lcd
    self.status_led = status_led
    self.rfid = rfid
    self.noise_hummer = noise_hummer
    self.current_mode = current_mode

    self.rfid.on_data_read_start = self._rfid_on_data_read_start
    self.rfid.on_data_read_end = self._rfid_on_data_read_end
    self.rfid.on_data_read_error = self._rfid_on_data_read_error
    self.rfid.on_data_write_start = self._rfid_on_data_write_start
    self.rfid.on_data_write_end = self._rfid_on_data_write_end
    
    self._print_mode()

    self.current_uid: str | None = None
  
  async def __display_for_time(self, text: str, time: int):
    self.lcd.write(text)
    await asyncio.sleep(time)
    self._print_mode()
  _display_for_time = run_task_factory(__display_for_time)

  async def __status_led_for_time(self, color: str, time: int):
    self.status_led.set_color(color)
    await asyncio.sleep(time)
    self.status_led.off()
  _status_led_for_time = run_task_factory(__status_led_for_time)

  def _rfid_on_data_read_start(self, uid: str):
    print("Data read start for UID: %s" % uid)
    self.status_led.set_color("0000ff")
    self.lcd.write("Reading data...")
    self.current_uid = uid

  def _rfid_on_data_read_end(self, data: str):
    print("Data read end: %s" % data)
    if self.current_uid is None:
      print("UID is not set")
      return
    access_control = AccessControl.from_record(self.current_uid, data)
    if(access_control.is_allowed()):
      self._status_led_for_time("00ff00", 5)
      self._display_for_time(f"{access_control.get_name()}\n{access_control.get_uid()} Granted", 5)
      self._buzz_ok()
    else:
      self._status_led_for_time("ff0000", 5)
      self._display_for_time(f"{access_control.get_name()}\n{access_control.get_uid()} Denied", 5)
      self._buzz_denied()

  def _rfid_on_data_read_error(self, error: str):
    print("Data read error: %s" % error)
    self._status_led_for_time("ff0000", 5)
    self._display_for_time("Data Read Error", 5)
    self._buzz_error()

  def _rfid_on_data_write_start(self, uid: str):
    print("Data write start for UID: %s" % uid)
    self.status_led.set_color("0000ff")
    self.lcd.write("Writing data...")

  def _rfid_on_data_write_end(self):
    print("Data write end")
    self._status_led_for_time("00ff00", 5)
    self._display_for_time("Data Written", 5)
    self._buzz_ok()

  def _rfid_on_data_write_error(self, error: str):
    print("Data write error: %s" % error)
    self._status_led_for_time("ff0000", 5)
    self._display_for_time("Data Write Error", 5)
    self._buzz_error()

  def _print_mode(self):
    if (self.current_mode == "read"):
      self.lcd.write("Mode: Read")
    elif (self.current_mode == "write"):
      self.lcd.write("Mode: Write")
  
  async def __buzz_ok(self):
    self.noise_hummer.buzz(440)
    await asyncio.sleep(0.25)
    self.noise_hummer.buzz(880)
    await asyncio.sleep(0.25)
    self.noise_hummer.stop()
  _buzz_ok = run_task_factory(__buzz_ok)

  async def __buzz_error(self):
    self.noise_hummer.buzz(440)
    await asyncio.sleep(1)
    self.noise_hummer.stop()
  _buzz_error = run_task_factory(__buzz_error)

  async def __buzz_denied(self):
    count = 5
    for i in range(count):
      self.noise_hummer.buzz(440)
      await asyncio.sleep(0.5)
      self.noise_hummer.stop()
      if i < count - 1:
        await asyncio.sleep(0.25)
  _buzz_denied = run_task_factory(__buzz_denied)

  async def main_loop(self):
    self._display_for_time("Hello.", 5)
    self._status_led_for_time("ffffff", 5)
    self._buzz_ok()
    try:
      while True:
        if(self.current_mode == "read"):
          data = self.rfid.read()
        elif(self.current_mode == "write"):
          data = AccessControl("0000000000", False, "Alexander Klein").to_record()
          self.rfid.write(data)
        await asyncio.sleep(0)
    except KeyboardInterrupt:
      print("KeyboardInterrupt")
      self.lcd.write("Goodbye.")
      self.status_led.off()
      self.noise_hummer.stop()
      print("Exiting main loop")
      raise KeyboardInterrupt
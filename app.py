from lcd import LCD
from rfid import RFID
from status_led import StatusLed
from noise_hummer import NoiseHummer
import asyncio
from util import run_task_factory

class App:
  def __init__(self, lcd: LCD, status_led: StatusLed, rfid: RFID, noise_hummer: NoiseHummer, current_mode: str = "read"):
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
    self.status_led.set_color("ffeb3b")
    self.lcd.write("Reading data...")

  def _rfid_on_data_read_end(self, data: str):
    print("Data read end: %s" % data)
    self._status_led_for_time("00ff00", 5)
    self._display_for_time("Data Read", 5)
    self._humm_ok()

  def _rfid_on_data_read_error(self, error: str):
    print("Data read error: %s" % error)
    self._status_led_for_time("ff0000", 5)
    self._display_for_time("Data Read Error", 5)
    self._humm_error()

  def _rfid_on_data_write_start(self, uid: str):
    print("Data write start for UID: %s" % uid)
    self.status_led.set_color("ffeb3b")
    self.lcd.write("Writing data...")

  def _rfid_on_data_write_end(self):
    self._status_led_for_time("00ff00", 5)
    self._display_for_time("Data Written", 5)
    self._humm_ok()

  def _rfid_on_data_write_error(self, error: str):
    print("Data write error: %s" % error)
    self._status_led_for_time("ff0000", 5)
    self._display_for_time("Data Write Error", 5)
    self._humm_error()

  def _print_mode(self):
    if (self.current_mode == "read"):
      self.lcd.write("Mode: Read")
    elif (self.current_mode == "write"):
      self.lcd.write("Mode: Write")
  
  async def __humm_ok(self):
    self.noise_hummer.hum(440)
    await asyncio.sleep(0.25)
    self.noise_hummer.hum(880)
    await asyncio.sleep(0.25)
    self.noise_hummer.stop()
  _humm_ok = run_task_factory(__humm_ok)

  async def __humm_error(self):
    self.noise_hummer.hum(440)
    await asyncio.sleep(1)
    self.noise_hummer.stop()
  _humm_error = run_task_factory(__humm_error)

  async def main_loop(self):
    self._display_for_time("Hello :)", 5)
    self._status_led_for_time("ffffff", 5)
    self._humm_ok()
    
    while True:
      if(self.current_mode == "read"):
        data = self.rfid.read()
      elif(self.current_mode == "write"):
        data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. Praesent egestas leo in pede. Praesent."
        self.rfid.write(data)
      await asyncio.sleep(0)
from machine import Pin, PWM

from time import sleep

class Buzzer:
  def __init__(self):
    self._pin = Pin(0, Pin.OUT)
    self._pwm = PWM(self._pin)

  def buzz(self, frequency: int, duty_u16: int = 65535 // 2):
    self._pwm.freq(frequency)
    self._pwm.duty_u16(duty_u16)
  
  def stop(self):
    self._pwm.duty_u16(0)

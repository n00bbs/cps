from machine import Pin, PWM

class StatusLed:
    BASE_FREQUENCY = 1000

    def __init__(self):
        self._red = Pin(1, Pin.OUT)
        self._green = Pin(2, Pin.OUT)
        self._blue = Pin(3, Pin.OUT)

        self._red_pwm = PWM(self._red, freq=self.BASE_FREQUENCY)
        self._green_pwm = PWM(self._green, freq=self.BASE_FREQUENCY)
        self._blue_pwm = PWM(self._blue, freq=self.BASE_FREQUENCY)

        self.color = self._parse_color("ffffff")
        self._update_color()
    
    def _parse_color(self, color: str) -> list:
        return [int(color[i:i+2], 16) for i in range(0, len(color), 2)]
    
    def _update_color(self):
        self._red_pwm.duty_u16(self.color[0] * 256)
        self._green_pwm.duty_u16(self.color[1] * 256)
        self._blue_pwm.duty_u16(self.color[2] * 256)

    def set_color(self, color: str):
        self.color = self._parse_color(color)
        self._update_color()
    
    def off(self):
        self._red_pwm.duty_u16(0)
        self._green_pwm.duty_u16(0)
        self._blue_pwm.duty_u16(0)
    
    def on(self):
        self._update_color()
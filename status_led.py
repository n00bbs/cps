from machine import Pin, PWM

class StatusLed:
    BASE_FREQUENCY = 1000

    COLOR_CORRECTION_RED = 1
    COLOR_CORRECTION_GREEN = 0.025
    COLOR_CORRECTION_BLUE = 0.2

    def __init__(self, red: int = 1, green: int = 2, blue: int = 3):
        self._red = Pin(red, Pin.OUT)
        self._green = Pin(green, Pin.OUT)
        self._blue = Pin(blue, Pin.OUT)

        self._red_pwm = PWM(self._red, freq=self.BASE_FREQUENCY)
        self._green_pwm = PWM(self._green, freq=self.BASE_FREQUENCY)
        self._blue_pwm = PWM(self._blue, freq=self.BASE_FREQUENCY)

        self.color = self._parse_color("ffffff")
        self._update_color()
    
    def _parse_color(self, color: str) -> list:
        # return [int(color[i:i+2], 16) for i in range(0, len(color), 2)]
        parsed_color = []
        for i in range(0, 6, 2):
            color_part = color[i:i+2]
            int_color_part = int(color_part, 16)
            parsed_color.append(int_color_part)
        return parsed_color
    
    def _update_color(self):
        self._red_pwm.duty_u16(int(self.color[0] * self.COLOR_CORRECTION_RED * 256))
        self._green_pwm.duty_u16(int(self.color[1] * self.COLOR_CORRECTION_GREEN * 256))
        self._blue_pwm.duty_u16(int(self.color[2] * self.COLOR_CORRECTION_BLUE * 256))

    def set_color(self, color: str):
        self.color = self._parse_color(color)
        self._update_color()
    
    def off(self):
        self._red_pwm.duty_u16(0)
        self._green_pwm.duty_u16(0)
        self._blue_pwm.duty_u16(0)
    
    def on(self):
        self._update_color()
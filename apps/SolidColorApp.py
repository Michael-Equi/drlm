import time

from drlm_app.drlm_app import DrlmApp
from drlm_common.datatypes import Color


class SolidColor(DrlmApp):
    def __init__(self, color: Color, ranges = [], host: str = 'localhost', port: int = 5555):
        super().__init__(host, port)
        self.color = color
        self.ranges = ranges

    def run(self):
        if len(self.ranges) == 0:
            for i in range(self.num_leds):
                self.strip.set_led(i, self.color)
        else:
            for lower, upper in self.ranges:
                assert lower > 0 and lower <= self.num_leds
                assert upper >= lower and upper <= self.num_leds
                for i in range(lower - 1, upper):
                    self.strip.set_led(i, self.color)
        while True:
            self.write()
            time.sleep(10)


if __name__ == "__main__":
    app = SolidColor(Color.from_rgb(255, 0, 0))
    app.run()
    app.close()

import time

from drlm_app.drlm_app import DrlmApp
from drlm_common.datatypes import Color


class SolidColor(DrlmApp):
    def __init__(self, color: Color, host: str = 'localhost', port: int = 5555):
        super().__init__(host, port)
        self.color = color

    def run(self):
        for i in range(self.num_leds):
            self.strip.set_led(i, self.color)
        self.write()


if __name__ == "__main__":
    app = SolidColor(Color.from_rgb(255, 0, 0))
    app.run()
    app.close()

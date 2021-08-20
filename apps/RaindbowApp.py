import time

import numpy as np

from drlm_app.drlm_app import DrlmApp
from drlm_common.datatypes import Color


class RainbowApp(DrlmApp):
    def __init__(self, speed=1000, host: str = 'localhost', port: int = 5555):
        super().__init__(host, port)
        self.speed = speed

    def run(self):
        num_segments = 3
        seg_length = int(self.num_leds / num_segments)
        decreasing = -np.arange(-1, 0, 1 / seg_length)
        increasing = np.arange(0, 1, 1 / seg_length)
        zero = np.zeros(seg_length)
        r = np.hstack((decreasing, zero, increasing))
        g = np.hstack((increasing, decreasing, zero))
        b = np.hstack((zero, increasing, decreasing))
        for i in range(self.num_leds):
            self.strip.set_led(i, Color.from_rgb(int(255 * r[i]), int(255 * g[i]), int(255 * b[i])))

        while True:
            self.strip.set(np.roll(self.strip.arr, 1))
            self.write()
            time.sleep(1 / int(self.speed))


if __name__ == "__main__":
    app = RainbowApp()
    app.run()
    app.close()

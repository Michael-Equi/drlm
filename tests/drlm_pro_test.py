import time
import numpy as np

from util import rgbToHex
from hw_interfaces import ProController

NUM_PIXELS = 288

if __name__ == "__main__":
    c = ProController(numPixels=NUM_PIXELS)
    # leds = np.zeros(NUM_PIXELS, np.int32)
    # leds[0] = rgbToHex(0, 10, 0)
    # R
    # leds[0] = 0xFF0000
    # G
    # leds[0] = 0x00FF00
    # B
    # leds[0] = 0x0000FF

    leds = np.zeros(NUM_PIXELS, np.int32)
    # leds[:10] += rgbToHex(0, 50, 0)
    # leds[10:20] += rgbToHex(255, 0, 0)
    # leds[20:30] += rgbToHex(0, 0, 255)

    decreasing = -np.arange(-1, 0, 1/96)
    increasing = np.arange(0, 1, 1/96)
    zero = np.zeros(96)

    R = np.hstack((decreasing, zero, increasing))
    G = np.hstack((increasing, decreasing, zero))
    B = np.hstack((zero, increasing, decreasing))

    for i in range(288):
        leds[i] = rgbToHex(int(255*R[i]), int(255*G[i]), int(255*B[i]))



    # for i in range(288):
    #     R = int(255 * (1 - i / 144)) if i < 144 else 0
    #     G = int(255 * i / 144) if i < 144 else int(255 * (1 - (i - 144) / 144))
    #     B = int(255 * (i - 144) / 144) if i > 144 else 0
    #     leds[i] = rgbToHex(R, G, B)


    I = np.eye(288, dtype=np.int32)
    while True:
        c.set(leds)
        c.write()

        # np.random.shuffle(I)
        # leds = I @ leds

        leds = np.roll(leds, 1)

        time.sleep(0.01)

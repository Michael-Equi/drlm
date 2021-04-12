import serial
import time

import numpy as np

NUM_PIXELS = 288


class ProController:

    def __init__(self, numPixels=288, port='/dev/cu.usbmodem86998501', baud=115200):
        self.numPixels = numPixels
        self.bytes = bytearray(numPixels * 3 + 1)
        self.ser = serial.Serial(port, baud, timeout=0, parity=serial.PARITY_EVEN)

    def write(self):
        parity = 0
        for b in self.bytes[:-1]:
            parity ^= b
        self.bytes[-1] = parity
        self.ser.write(self.bytes)

    def setPixel(self, i, r, g, b):
        assert i < self.numPixels
        assert r < 256 and g < 256 and b < 256
        self.bytes[3 * i] = r
        self.bytes[3 * i + 1] = g
        self.bytes[3 * i + 2] = b

    def set(self, arr: np.ndarray):
        assert arr.size <= self.numPixels
        for i, c in enumerate(arr):
            bc = c.tobytes()
            self.bytes[3 * i] = bc[2]
            self.bytes[3 * i + 1] = bc[1]
            self.bytes[3 * i + 2] = bc[0]

    def clear(self):
        for i in range(len(self.bytes) - 1):
            self.bytes[i] = 0


def rgbToHex(r, g, b):
    assert r < 256 and g < 256 and b < 256
    return r << 16 | g << 8 | b


if __name__ == "__main__":
    c = ProController()
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

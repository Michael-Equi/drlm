import serial
import numpy as np


class Controller:

    def __init__(self, port='/dev/tty.usbmodem143301', baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0, parity=serial.PARITY_EVEN)

    def send(self, R, G, B):
        arr = bytearray([int(R), int(G), int(B), 0x0a])
        self.ser.write(arr)


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

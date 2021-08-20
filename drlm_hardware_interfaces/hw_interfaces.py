import numpy as np
import serial
import threading


class Controller:

    def __init__(self, port, num_pixels=288, baud=115200):
        self.numPixels = num_pixels
        self.bytes = bytearray(num_pixels * 3 + 1)
        self.ser = serial.Serial(port, baud, timeout=0, parity=serial.PARITY_EVEN)
        self.lock = threading.Lock()

    def write(self):
        with self.lock:
            parity = 0
            for b in self.bytes[:-1]:
                parity ^= b
            self.bytes[-1] = parity
            self.ser.write(self.bytes)

    def set_pixel(self, i, r, g, b):
        assert i < self.numPixels
        assert r < 256 and g < 256 and b < 256
        with self.lock:
            self.bytes[3 * i] = r
            self.bytes[3 * i + 1] = g
            self.bytes[3 * i + 2] = b

    def set(self, arr: np.ndarray):
        assert arr.size <= self.numPixels
        with self.lock:
            for i, c in enumerate(arr):
                bc = c.tobytes()
                self.bytes[3 * i] = bc[2]
                self.bytes[3 * i + 1] = bc[1]
                self.bytes[3 * i + 2] = bc[0]

    def clear(self):
        with self.lock:
            for i in range(len(self.bytes) - 1):
                self.bytes[i] = 0

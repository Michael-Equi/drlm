import threading
from abc import ABC, abstractmethod

import numpy as np
import pygame
import serial

from drlm_common.datatypes import LedStrip, Color


class DrlmController(ABC):

    def __init__(self, num_leds: int = 288):
        self.num_leds = num_leds

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def set_pixel(self, i: int, color: Color):
        pass

    @abstractmethod
    def set(self, arr: np.ndarray):
        pass

    @abstractmethod
    def clear(self):
        pass


class DrlmSimController(DrlmController):

    def __init__(self, num_leds: int = 288):
        super().__init__(num_leds)
        pygame.init()
        self.display = pygame.display.set_mode((1080, 720))
        self.display.fill((0, 0, 0))
        pygame.display.update()

        self.strip = LedStrip(num_leds)

    def write(self):
        radius = 5
        buffer = 4

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        self.display.fill((0, 0, 0))

        leds_per_row = int(self.display.get_width() // (2 * radius + buffer)) - 1
        for i, led in enumerate(self.strip):
            location = ((i % leds_per_row + 1) * (2 * radius + buffer), (i // leds_per_row + 1) * (2 * radius + buffer))
            pygame.draw.circle(self.display, led.get_rgb(), location, radius, 2 * radius)

        pygame.display.update()

    def set_pixel(self, i: int, color: Color):
        self.strip.set_led(i, color)

    def set(self, arr: np.ndarray):
        assert len(self.strip) == len(arr)
        self.strip.set(arr)

    def clear(self):
        self.strip.set(np.zeros(len(self.strip), dtype=np.int32))


class DrlmHardwareController(DrlmController):

    def __init__(self, port, num_leds=288, baud=115200):
        super().__init__(num_leds)
        self.bytes = bytearray(num_leds * 3 + 1)
        self.ser = serial.Serial(port, baud, timeout=0, parity=serial.PARITY_EVEN)
        self.lock = threading.Lock()

    def write(self):
        with self.lock:
            parity = 0
            for b in self.bytes[:-1]:
                parity ^= b
            self.bytes[-1] = parity
            self.ser.write(self.bytes)

    def set_pixel(self, i: int, color: Color):
        assert i < self.num_leds
        r, g, b = color.get_rgb()
        with self.lock:
            self.bytes[3 * i] = r
            self.bytes[3 * i + 1] = g
            self.bytes[3 * i + 2] = b

    def set(self, arr: np.ndarray):
        assert arr.size <= self.num_leds
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

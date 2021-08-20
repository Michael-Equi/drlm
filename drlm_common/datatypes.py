import numpy as np

from drlm_common.utils import hex_to_rgb, rgb_to_hex


class Color:

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int):
        return cls(rgb_to_hex(r, g, b))

    def __init__(self, color):
        self.color = color

    def set_rgb(self, r: int, g: int, b: int):
        self.color = rgb_to_hex(r, g, b)

    def set_hex(self, color: int):
        self.color = color

    def get_rgb(self):
        return hex_to_rgb(self.color)

    def get_hex(self):
        return self.color


class LedStrip:

    def __init__(self, length: int):
        self.arr = np.zeros(length, np.int32)

    def __len__(self):
        return len(self.arr)

    def __iter__(self):
        return map(Color, self.arr)

    def get_led(self, i: int) -> Color:
        return Color(self.arr[i])

    def set_led(self, i, color: Color):
        self.arr[i] = color.get_hex()

    def set(self, arr: np.ndarray):
        assert self.arr.shape == arr.shape
        self.arr = arr

    def bytes(self):
        return self.arr.tobytes('C')

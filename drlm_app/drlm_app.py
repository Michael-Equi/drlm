import json
import socket
import time
from abc import ABC, abstractmethod

from drlm_common.datatypes import Color, LedStrip


class DrlmApp(ABC):

    def __init__(self, host: str = 'localhost', port: int = 5555):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((host, port))
        except ConnectionRefusedError:
            print("Connection refused to", host, 'on port', port, '. Make sure DRLM Core is running.')
            quit()

        cfg = json.loads(self.s.recv(2048))
        self.num_leds = cfg['num_leds']
        self.header_length = cfg['header_length']
        self.max_rate = cfg['max_rate']

        self.strip = LedStrip(self.num_leds)

        self.last_write = 0

    def create_packet(self, data: bytes) -> bytes:
        header = bytes(f'{len(data):<{self.header_length}}', 'utf-8')
        return header + data

    def write(self) -> bool:
        # Rate limit
        if time.time() - self.last_write > 1 / self.max_rate:
            self.s.send(self.create_packet(self.strip.bytes()))
            self.last_write = time.time()
            return True
        return False

    def close(self):
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()

    @abstractmethod
    def run(self):
        pass


class DemoApp(DrlmApp):
    def run(self):
        for i in range(len(self.strip)):
            self.strip.set_led(i, Color.from_rgb(255, 0, 0))
            self.write()
            time.sleep(0.1)
        for i in range(len(self.strip)):
            self.strip.set_led(i, Color.from_rgb(0, 0, 0))
            self.write()
            time.sleep(0.1)

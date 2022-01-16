import json
import socket
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

from drlm_controllers.drlm_controller import DrlmController, DrlmHardwareController


@dataclass
class DrlmCoreConfig:
    host: str = 'localhost'
    port: int = 5555
    header_length: int = 10
    num_leds: int = 576
    buffer_size: int = 4096


class DrlmCore:

    @staticmethod
    def _parse_packet(length, data):
        return data[:length], data[length:]

    def __init__(self, controller: DrlmController, config: DrlmCoreConfig):
        self.config = config
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.config.host, self.config.port))
        self.socket.listen(1)

        self.connection: Optional[socket.socket] = None

        self.controller = controller
        self.controller.write()

        # Estimate the max update rate
        n_samples = 50
        margin = 0.3
        s = time.time()
        for _ in range(n_samples):
            self.controller.write()
        t = (time.time() - s) / n_samples
        self.max_rate = (1 - margin) * (1 / t)

        print('Starting DRLM Core on', self.config.host, 'with port', self.config.port)
        print(f'Max update rate: {self.max_rate:0.2f}Hz')

    def _create_packet(self, data: bytes) -> bytes:
        header = bytes(f'{len(data):<{self.config.header_length}}', 'utf-8')
        return header + data

    def _send_config(self):
        assert self.connection is not None
        config = bytes(json.dumps({"num_leds": self.config.num_leds,
                                   "header_length": self.config.header_length,
                                   "max_rate": self.max_rate}),
                       'utf-8')
        self.connection.send(config)

    def _parse_data(self, data):
        return int(data[:self.config.header_length]), data[self.config.header_length:]

    def _close(self):
        if self.connection is not None:
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()

    def run(self):
        try:
            while True:
                self.connection, address = self.socket.accept()
                print('New connection received from', address)
                self._send_config()
                data: bytes = bytes('', 'utf-8')
                data_len: Optional[int] = None  # Length of the incoming message, None means no message in progress
                while self.connection is not None:
                    data += self.connection.recv(self.config.buffer_size)
                    if data == bytes('', 'utf-8'):
                        self.connection = None
                        self.controller.clear()
                        self.controller.write()
                        print('Connection from', address, 'closed')
                    else:
                        if data_len is None and len(data) >= self.config.header_length:
                            data_len, data = self._parse_data(data)
                        if data_len is not None and len(data) >= data_len:
                            msg, data = self._parse_packet(data_len, data)
                            self.controller.set(np.frombuffer(msg, dtype=np.int32))
                            self.controller.write()
                            data_len = None
        except KeyboardInterrupt:
            self._close()
            print("DRLM Core Terminated")


if __name__ == "__main__":
    controller = DrlmHardwareController(port='/dev/cu.usbmodem86998501', num_leds=576)
    cfg = DrlmCoreConfig()
    drlm_core = DrlmCore(controller, cfg)
    drlm_core.run()

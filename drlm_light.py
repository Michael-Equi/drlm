import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

from dearpygui.core import *
from dearpygui.simple import *

import threading

import time
import util

import serial


def clipAndNormalize(s, m=3):
    s = np.clip(s, 0, np.average(s) * m)
    n = (s - np.min(s)) / (np.max(s) - np.min(s))
    return n

class Controller:

    def __init__(self, port='/dev/tty.usbmodem143301', baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0, parity=serial.PARITY_EVEN)

    def send(self, R, G, B):
        arr = bytearray([int(R), int(G), int(B), 0x0a])
        self.ser.write(arr)

class DRLMLight:

    def __init__(self, song="JukeboxHero"):
        self.y, self.sr, self.file = util.loadSongFromMp3(song)
        self.D = librosa.stft(self.y[0], n_fft=2048)
        self.start = None

        self.bass = clipAndNormalize(util.accumulateRange(self.D, 60, 250))
        self.midrange = clipAndNormalize(util.accumulateRange(self.D, 500, 2000))
        self.presence = clipAndNormalize(util.accumulateRange(self.D, 4000, 6000))

        self.controller = Controller()

        with window("DRLM Light"):
            add_drawing("Visualization", width=400, height=400)
            add_simple_plot("Frequencies Magnitude", source="freq_data", minscale=0.0, maxscale=np.max(np.abs(self.D)),
                            height=300)

        set_render_callback(self.onRender)
        start_dearpygui(primary_window="DRLM Light")

    def onRender(self):
        if not self.start:
            threading.Thread(target=util.playSong(self.file)).start()
            self.start = time.time()

        i = util.timeToBin(time.time() - self.start, self.D, self.sr)

        """
        Update Graph Data
        """
        set_value("freq_data", list(np.abs(self.D[:, i])))

        """
        Update Drawing
        """
        clear_drawing("Visualization")

        # Base
        R = 255 * self.bass[i]
        # Midrange
        G = 255 * self.midrange[i]
        # Presence
        B = 255 * self.presence[i]

        self.controller.send(R, G, B)

        draw_rectangle("Visualization", [0, 0], [200, 200], [0, 0, 0], fill=[R, G, B, 255], thickness=0)


if __name__ == "__main__":
    # songName = 'AWarriorsCall'
    # songName = 'Ministry-Jesus-Built-My-Hotrod'
    # songName = 'JukeboxHero'
    # songName = 'Thunderstruck'
    # songName = 'OneMoreTime'
    # songName = 'BornToRun'
    # songName = 'PlugWalk'
    # songName = 'Albatraoz'
    songName = 'MajorLazerLightitUpRemix'
    # songName = '2000Hz'
    # songName = '200Hz'
    #
    drlm = DRLMLight(songName)

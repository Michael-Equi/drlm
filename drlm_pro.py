import os
import numpy as np
import librosa
import librosa.display

from dearpygui.core import *
from dearpygui.simple import *

import threading

import time
import util

from hw_interfaces import ProController
import generators

NUM_PIXELS = 288


class DRLMPro:

    def __init__(self, song="JukeboxHero"):
        self.y, self.sr, self.file = util.loadSongFromMp3(song)
        self.D = librosa.stft(self.y[0], n_fft=2048)
        self.start = None

        self.generator = generators.RGBGenerator(288, self.D, self.sr)
        self.controller = ProController(numPixels=NUM_PIXELS)

        with window("DRLM Light"):
            for i in range(NUM_PIXELS):
                if i % 50 != 0:
                    add_same_line(name="sl" + str(i), spacing=0)
                add_drawing("Visualization_" + str(i), width=20, height=20)
            add_simple_plot("Frequencies Magnitude", source="freq_data", minscale=0.0, maxscale=np.max(np.abs(self.D)),
                            height=300)

        set_render_callback(self.onRender)
        start_dearpygui(primary_window="DRLM Light")

    def onRender(self):
        if not self.start:
            threading.Thread(target=util.playSong(self.file)).start()
            self.start = time.time()

        t = time.time() - self.start
        i = util.timeToBin(t, self.D, self.sr)

        """
        Update Graph Data
        """
        set_value("freq_data", list(np.abs(self.D[:, i])))

        """
        Update Drawing
        """
        clear_drawing("Visualization")

        c = self.generator.sample(t)
        self.controller.set(c)
        self.controller.write()

        for i in range(NUM_PIXELS):
            R, G, B = util.hexToRGB(c[i])
            draw_rectangle("Visualization_" + str(i), [0, 0], [20, 20], [0, 0, 0], fill=[R, G, B, 255], thickness=0)


if __name__ == "__main__":
    # songName = 'AWarriorsCall'
    # songName = 'Ministry-Jesus-Built-My-Hotrod'
    # songName = 'JukeboxHero'
    # songName = 'Thunderstruck'
    # songName = 'OneMoreTime'
    # songName = 'BornToRun'
    # songName = 'PlugWalk'
    songName = 'Albatraoz'
    # songName = 'MajorLazerLightitUpRemix'
    # songName = '2000Hz'
    # songName = '200Hz'

    drlm = DRLMPro(os.path.join('music', songName))

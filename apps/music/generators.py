import abc

import numpy as np
import utils

from drlm_common.datatypes import Color


class Generator(abc.ABC):
    """
    @param D output of stft on the audio signal
    """

    def __init__(self, numPixels: int, D: np.ndarray, sr: int):
        self.num_pixels = numPixels
        self.D = D
        self.sr = sr

    """
    @return array of LED RGB values sampled for time t
    """

    def sample(self, t: float) -> np.ndarray:
        pass


class RGBGenerator(Generator):
    def __init__(self, num_leds, D, sr, curve=3):
        super(RGBGenerator, self).__init__(num_leds, D, sr)
        self.curve = curve
        self.bass = utils.clip_and_normalize(utils.accumulate_range(self.D, 60, 250))
        self.midrange = utils.clip_and_normalize(utils.accumulate_range(self.D, 500, 2000))
        self.presence = utils.clip_and_normalize(utils.accumulate_range(self.D, 4000, 6000))

    def sample(self, t):
        i = utils.time_to_bin(t, self.D, self.sr)
        # Base
        R = int(255 * self.bass[i] ** self.curve)
        # Midrange
        G = int(255 * self.midrange[i] ** self.curve)
        # Presence
        B = int(255 * self.presence[i] ** self.curve)

        v = Color.from_rgb(R, G, B).get_hex()
        arr = np.zeros(self.num_pixels, dtype=np.int32)
        for i in range(arr.size):
            arr[i] = v

        return arr


class PulseGenerator(Generator):
    def __init__(self, num_leds, D, sr, curve=3):
        super(PulseGenerator, self).__init__(num_leds, D, sr)
        self.curve = curve
        self.bass = utils.clip_and_normalize(utils.accumulate_range(self.D, 60, 250))
        self.midrange = utils.clip_and_normalize(utils.accumulate_range(self.D, 500, 2000))
        self.presence = utils.clip_and_normalize(utils.accumulate_range(self.D, 4000, 6000))

        self.arr = np.zeros(self.num_pixels, dtype=np.int32)

    def sample(self, t):
        i = utils.time_to_bin(t, self.D, self.sr)
        # Base
        R = int(255 * self.bass[i] ** self.curve)
        # Midrange
        G = int(255 * self.midrange[i] ** self.curve)
        # Presence
        B = int(255 * self.presence[i] ** self.curve)

        v = Color.from_rgb(R, G, B).get_hex()
        self.arr = np.roll(self.arr, 1)
        self.arr[0] = v

        return self.arr


class WaveGenerator(Generator):
    def __init__(self, num_leds, D, sr):
        super(WaveGenerator, self).__init__(num_leds, D, sr)

        # generate cmap
        num_segments = 2
        seg_length = int(self.num_pixels / num_segments)
        decreasing = -np.arange(-1, 0, 1 / seg_length)
        increasing = np.arange(0, 1, 1 / seg_length)
        zero = np.zeros(seg_length)

        R = np.hstack((decreasing, zero))
        G = np.hstack((increasing, decreasing))
        B = np.hstack((zero, increasing))
        self.cmap = np.zeros(self.num_pixels, dtype=np.int32)
        for i in range(self.num_pixels):
            self.cmap[i] = Color.from_rgb(int(255 * R[i]), int(255 * G[i]), int(255 * B[i])).get_hex()

        self.smoothing = 10
        self.max_bin = 600

        avgs = np.average(np.abs(self.D), axis=1)[:self.max_bin]
        stds = np.std(np.abs(self.D), axis=1)[:self.max_bin]

        # filter sample
        fAvgs = np.convolve(avgs, np.ones(self.smoothing) / self.smoothing, mode='same')
        fStds = np.convolve(stds, np.ones(self.smoothing) / self.smoothing, mode='same')

        # subsample and crop
        fss = fAvgs[::int(np.floor(avgs.shape[0] / self.num_pixels))]
        crop = int((fss.shape[0] - self.num_pixels) / 2)
        self.cfss_avgs = fss[crop:-crop]

        fss = fStds[::int(np.floor(stds.shape[0] / self.num_pixels))]
        crop = int((fss.shape[0] - self.num_pixels) / 2)
        self.cfss_stds = fss[crop:-crop]

    def sample(self, t, center=144):

        i = utils.time_to_bin(t, self.D, self.sr)
        s = np.abs(self.D[:, i])[:self.max_bin]
        s = np.where(s < 0.1, 0, s)  # remove baseline noise

        # filter sample
        fs = np.convolve(s, np.ones(self.smoothing) / self.smoothing, mode='same')

        # subsample and crop
        fss = fs[::int(np.floor(s.shape[0] / self.num_pixels))]
        crop = int((fss.shape[0] - self.num_pixels) / 2)
        cfss = fss[crop:-crop]

        # normalize
        # ncfss = ((cfss - np.min(cfss)) / (np.max(cfss) - np.min(cfss))) ** 3
        ncfss = np.clip(cfss / (self.cfss_avgs + 5 * self.cfss_stds), 0, 1)

        arr = np.zeros(self.num_pixels, dtype=np.int32)
        for i in range(arr.size):
            R, G, B = Color(self.cmap[i]).get_rgb()
            if np.isnan(ncfss[i]):
                arr[i] = 0
            else:
                arr[i] = Color.from_rgb(int(ncfss[i] * R), int(ncfss[i] * G), int(ncfss[i] * B)).get_hex()

        return arr

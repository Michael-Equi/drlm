import abc
import numpy as np
import util


class Generator(abc.ABC):
    """
    @param D output of stft on the audio signal
    """

    def __init__(self, numPixels: int, D: np.ndarray, sr: int):
        self.numPixels = numPixels
        self.D = D
        self.sr = sr

    """
    @return array of LED RGB values sampled for time t
    """

    def sample(self, t: float) -> np.ndarray:
        pass


class RGBGenerator(Generator):
    def __init__(self, numPixels, D, sr, curve=3):
        super(RGBGenerator, self).__init__(numPixels, D, sr)
        self.curve = curve
        self.bass = util.clipAndNormalize(util.accumulateRange(self.D, 60, 250))
        self.midrange = util.clipAndNormalize(util.accumulateRange(self.D, 500, 2000))
        self.presence = util.clipAndNormalize(util.accumulateRange(self.D, 4000, 6000))

    def sample(self, t):
        i = util.timeToBin(t, self.D, self.sr)
        # Base
        R = int(255 * self.bass[i] ** self.curve)
        # Midrange
        G = int(255 * self.midrange[i] ** self.curve)
        # Presence
        B = int(255 * self.presence[i] ** self.curve)

        v = util.rgbToHex(R, G, B)
        arr = np.zeros(self.numPixels, dtype=np.int32)
        for i in range(arr.size):
            arr[i] = v

        return arr


import sys


class WaveGenerator(Generator):
    def __init__(self, numPixels, D, sr):
        super(WaveGenerator, self).__init__(numPixels, D, sr)

        # generate cmap
        numSegments = 2
        segLength = int(self.numPixels / numSegments)
        decreasing = -np.arange(-1, 0, 1 / segLength)
        increasing = np.arange(0, 1, 1 / segLength)
        zero = np.zeros(segLength)
        R = np.hstack((decreasing, zero))
        G = np.hstack((increasing, decreasing))
        B = np.hstack((zero, increasing))
        self.cmap = np.zeros(self.numPixels, dtype=np.int32)
        for i in range(self.numPixels):
            self.cmap[i] = util.rgbToHex(int(255 * R[i]), int(255 * G[i]), int(255 * B[i]))

    def sample(self, t, center=144):
        i = util.timeToBin(t, self.D, self.sr)

        smoothing = 100
        s = np.abs(self.D[:, i])[:800]

        # filter sample
        fs = np.convolve(s, np.ones(smoothing) / smoothing, mode='same')

        # subsample and crop
        fss = fs[::int(np.floor(s.shape[0] / self.numPixels))]
        crop = int((fss.shape[0] - self.numPixels) / 2)
        cfss = fss[crop:-crop]

        # normalize
        ncfss = ((cfss - np.min(cfss)) / (np.max(cfss) - np.min(cfss)))**3

        arr = np.zeros(self.numPixels, dtype=np.int32)
        for i in range(arr.size):
            R, G, B = util.hexToRGB(self.cmap[i])
            if np.isnan(ncfss[i]):
                arr[i] = 0
            else:
                arr[i] = util.rgbToHex(int(ncfss[i] * R), int(ncfss[i] * G), int(ncfss[i] * B))

        return arr

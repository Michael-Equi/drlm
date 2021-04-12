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
        R = int(255 * self.bass[i]**self.curve)
        # Midrange
        G = int(255 * self.midrange[i]**self.curve)
        # Presence
        B = int(255 * self.presence[i]**self.curve)

        v = util.rgbToHex(R, G, B)
        arr = np.zeros(self.numPixels, dtype=np.int32)
        for i in range(arr.size):
            arr[i] = v

        return arr
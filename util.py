from pathlib import Path
from pygame import mixer
import librosa
import numpy as np
import os


def binToFreq(n: int, sampleFreq: int = 22050, nBins: int = 2048):
    # sample rate of 22050 Hz
    # n_fft=2048 samples, corresponds to a physical duration of 93 milliseconds
    return n * sampleFreq / nBins


def freqToBin(f: float, sampleFreq: int = 22050, nBins: int = 2048):
    # sample rate of 22050 Hz
    # n_fft=2048 samples, corresponds to a physical duration of 93 milliseconds
    return int(round(f * (nBins / sampleFreq)))


def getTimes(D: np.ndarray, sr: int, hop_length=512, n_fft=2048):
    return librosa.frames_to_time(np.arange(0, D.shape[1], 1), sr=sr, hop_length=hop_length, n_fft=n_fft)


def accumulateRange(D: np.ndarray, fBottom: float, fTop: float):
    assert fBottom >= 0 and fTop <= binToFreq(D.shape[0])
    bottomBin = freqToBin(fBottom)
    topBin = freqToBin(fTop)
    s = np.sum(np.abs(D[bottomBin:topBin, :]), axis=0)
    return s


def binsByMagnitude(D: np.ndarray):
    maximums = np.max(np.abs(D), axis=1)
    maxBins = []
    for i in range(D.shape[0]):
        b = np.argmax(maximums)
        maximums[b] = 0
        maxBins.append(b)
    return maxBins


def freqsByMagnitude(D: np.ndarray):
    maxFreqs = []
    bins = binsByMagnitude(D)
    for b in bins:
        maxFreqs.append(binToFreq(b))
    return maxFreqs


def listSongs(path: Path = Path(os.path.dirname(__file__), "music")):
    return [f.name for f in path.iterdir() if ".mp3" in f.name]


def loadSongFromMp3(song: str, path: Path = Path(os.path.dirname(__file__), "music")):
    songPath = path.joinpath(song)
    song_mp3 = Path(str(songPath) + ".mp3")

    if not song_mp3.exists():
        print(song, "mp3 not found")
        print("mp3 files in", path, "are", listSongs(path))
        raise FileNotFoundError

    song_y_npy = Path(str(songPath) + "_y.npy")
    song_sr_npy = Path(str(songPath) + "_sr.npy")

    y, sr = None, None
    if song_y_npy.exists() and song_sr_npy.exists():
        y = np.load(song_y_npy)
        sr = np.load(song_sr_npy)
    else:
        y, sr = librosa.load(song_mp3, mono=False)
        np.save(song_y_npy, y)
        np.save(song_sr_npy, sr)

    return y, sr, song_mp3


def rgbToHex(r, g, b):
    assert r < 256 and g < 256 and b < 256
    return r << 16 | g << 8 | b


def hexToRGB(v):
    return (v >> 16) & 0b11111111, (v >> 8) & 0b11111111, v & 0b11111111


def clipAndNormalize(s, m=3):
    s = np.clip(s, 0, np.average(s) * m)
    n = (s - np.min(s)) / (np.max(s) - np.min(s))
    return n


def timeToBin(time, D, sr):
    return np.argmin(np.abs(getTimes(D, sr) - time))


def playSong(file: Path):
    mixer.init()
    mixer.music.load(str(file))
    mixer.music.play()

import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

from dearpygui.core import *
from dearpygui.simple import *

from pygame import mixer

import threading

import time

start = None
beats = None
file = None
times = None
fft = None


def onRender():
    global beats, start, file, fft, times
    clear_drawing("Visualization")
    if not start:
        threading.Thread(target=playSong(file)).start()
        start = time.time()

    # if np.min(np.abs(beats - (time.time() - start))) < 0.05:
    #     draw_circle("Visualization", center=[200, 200], radius=10, thickness=5, color=[255, 255, 255])

    if np.min(np.abs(times - (time.time() - start))) < 0.005:
        if fft[np.argmin(np.abs(times - (time.time() - start)))] > np.average(fft) * 1.2:
            draw_circle("Visualization", center=[200, 200], radius=10, thickness=5, color=[255, 255, 255])


def bin_to_freq(n, sampleFreq=22050, nBins=2048):
    # sample rate of 22050 Hz
    # n_fft=2048 samples, corresponds to a physical duration of 93 milliseconds
    return n * sampleFreq / nBins


def freq_to_bin(f, sampleFreq=22050, nBins=2048):
    # sample rate of 22050 Hz
    # n_fft=2048 samples, corresponds to a physical duration of 93 milliseconds
    return round(f * (nBins / sampleFreq))

def playSong(file):
    mixer.init()
    mixer.music.load(file)
    mixer.music.play()


def main(song):
    global beats, file, times, fft

    song_y_npy = Path(song + "_y.npy")
    song_sr_npy = Path(song + "_sr.npy")
    song_mp3 = Path(song + ".mp3")
    file = song_mp3

    y, sr = None, None

    if song_y_npy.exists() and song_sr_npy.exists():
        y = np.load(song_y_npy)
        sr = np.load(song_sr_npy)
    else:
        y, sr = librosa.load(song_mp3, mono=False)
        np.save(song_y_npy, y)
        np.save(song_sr_npy, sr)

    print("Base:", freq_to_bin(60), freq_to_bin(250))
    print(bin_to_freq(1025))

    # tempo, beats = librosa.beat.beat_track(y[0], sr, units="time")
    # print("tempo", tempo)
    # print(beats)
    # print(beats[0] - beats[1])
    # print(beats[1] - beats[2])

    # print(y.shape)
    # default hop length = n_fft // 4
    # rows in D = (1 + n_fft/2)
    D = librosa.stft(y[0], n_fft=2048)
    print(D.shape)
    times = librosa.frames_to_time(np.arange(0, D.shape[1], 1), sr=sr, hop_length=512, n_fft=2048)
    print("max freq:", bin_to_freq(np.argmax(np.max(np.abs(D), axis=1))))

    maximums = np.max(np.abs(D), axis=1)
    max_bins = []
    for i in range(10):
        bin = np.argmax(maximums)
        maximums[bin] = 0
        max_bins.append(bin)
    print(max_bins)

    max_freqs = []
    for i in max_bins:
        max_freqs.append(bin_to_freq(i))
    print(max_freqs)

    fft = np.zeros(D[0].shape)
    for i in range(freq_to_bin(60), freq_to_bin(250)):
        fft += np.abs(D[i])

    # fft = np.abs(D[7])
    print(np.min(fft), np.max(fft), np.average(fft))

    plt.plot(fft)
    plt.show()
    #
    # print(np.max(D))

    # plt.plot(y)
    # plt.show()

    with window("DRLM Window"):
        add_drawing("Visualization", width=400, height=400)

    set_render_callback(onRender)

    start_dearpygui(primary_window="DRLM Window")

    print(y.shape)


if __name__ == "__main__":
    # songName = 'Ministry-Jesus-Built-My-Hotrod'
    songName = 'JukeboxHero'
    # songName = '2000Hz'
    # songName = '200Hz'

    main(songName)

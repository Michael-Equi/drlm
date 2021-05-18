import pyaudio
import librosa
import util

import numpy as np
import matplotlib.pyplot as plt
from pygame import mixer

import time

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 1024
RECORD_SECONDS = 2
WAVE_OUTPUT_FILENAME = "file.wav"

audio = pyaudio.PyAudio()

y, sr, file = util.loadSongFromMp3("JukeBoxHero")
mixer.init()
mixer.music.load(str(file))
mixer.music.play()

time.sleep(3)


# start Recording
stream = audio.open(input_device_index=2,
                    format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("recording...")
frames = []
arr = np.array([])

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    a = np.frombuffer(data, dtype=np.int16)
    arr = np.append(arr, a)
    frames.append(data)

arr /= np.iinfo(np.int16).max
print("finished recording")

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

mixer.music.stop()

sample = arr
raw = y[0]

DRaw = librosa.stft(raw, n_fft=2048)
DSample = librosa.stft(sample, n_fft=2048)

print(DRaw.shape, DSample.shape)
max = -9999
argmax = -1
for i in range(DRaw.shape[1]//DSample.shape[1]):
    d = DRaw[:, i*DSample.shape[1]:(i+1)*DSample.shape[1]]@DSample
    dnorm = np.linalg.norm(d)
    if dnorm > max:
        max = dnorm
        argmax = i

print(argmax)

# c = np.convolve(arr[:22050], y[0, :22050*10], mode='same')
# print(np.argmax(c)/22050)
# fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
# fig.suptitle('Horizontally stacked subplots')
# ax1.plot(arr)
# ax2.plot(y[0, :22050*3])
# ax3.plot(c)
# plt.show()
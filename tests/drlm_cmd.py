import os
import time
import serial.tools.list_ports
import numpy as np
from pydantic import BaseModel, Field
import threading
from queue import Queue

from hw_interfaces import ProController
import util

NUM_PIXELS = 288


class ProcessMessage(BaseModel):
    stop: bool = Field(default=False)
    data: dict = Field(default={})


def sunClock(controller: ProController, queue: Queue):
    import datetime
    from suntime import Sun

    lat = 37.876630
    long = -122.249593
    sun = Sun(lat, long)

    while True:
        now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=7)  # WTF Jankery is this
        today_sr = sun.get_local_sunrise_time(now)
        today_ss = sun.get_local_sunset_time(now + datetime.timedelta(days=1))
        now -= datetime.timedelta(days=1)

        curve = 1 - np.arange(-1, 1, 1 / 48) ** 2
        animation = lambda x: -4 * x ** 2 + 4 * x
        morning = 0.1 * np.array([250, 80, 40])
        noon = 0.8 * np.array([255, 255, 255])
        # evening = 0.1*np.array([250, 40, 80])

        while True:
            if today_sr < now < today_ss:
                progress = (now - today_sr).seconds / (today_ss - today_sr).seconds
                center = round(controller.numPixels * progress)
                colors = np.zeros(controller.numPixels, np.int32)

                offset = curve.shape[0] // 2

                rangeL = max(0, center - offset)
                rangeH = min(controller.numPixels, center + offset)
                d = rangeH - rangeL
                colors[rangeL:rangeH] = \
                    255 * (morning * (1 - animation(progress)) + noon * animation(progress) * curve)[
                          (offset - d) // 2:(offset + d) // 2]

                # controller.set(colors)
            else:
                pass
                # controller.clear()

            now += datetime.timedelta(seconds=3600)

        # controller.write()
        time.sleep(0.1)


def oceanWave(controller: ProController, queue: Queue):
    import time
    peak = np.array([0, 150, 180])
    valley = np.array([0, 0, 20])

    x = np.arange(0, 1, 1 / (controller.numPixels * 2))
    f = np.sin(4 * np.pi * x) * np.sin(2 * np.pi * x)  # period of 2
    start = time.time()
    period = 10
    while True:
        a = np.sin(2 * np.pi * (time.time() - start) / period)
        fp = (1 - 1 / 2 * a * f[:controller.numPixels])
        for i, p in enumerate(fp):
            color = np.clip(p ** 2 * peak + (1 - p) ** 2 * valley, 0, 255)
            controller.set_pixel(i, int(color[0]), int(color[1]), int(color[2]))

        controller.write()
        f = np.roll(f, 1)
        time.sleep(0.01)


def rainbow(controller: ProController, queue: Queue, speed: str):
    import time
    # generate cmap
    numSegments = 3
    segLength = int(controller.numPixels / numSegments)
    decreasing = -np.arange(-1, 0, 1 / segLength)
    increasing = np.arange(0, 1, 1 / segLength)
    zero = np.zeros(segLength)
    R = np.hstack((decreasing, zero, increasing))
    G = np.hstack((increasing, decreasing, zero))
    B = np.hstack((zero, increasing, decreasing))
    cmap = np.zeros(controller.numPixels, dtype=np.int32)
    for i in range(controller.numPixels):
        cmap[i] = util.rgbToHex(int(255 * R[i]), int(255 * G[i]), int(255 * B[i]))

    lastMessage = ProcessMessage()
    while not lastMessage.stop:
        if not queue.empty():
            lastMessage = queue.get_nowait()
        cmap = np.roll(cmap, 1)
        controller.set(cmap)
        controller.write()
        time.sleep(1/int(speed))
    return True


def listSongs(controller: ProController, queue: Queue):
    print(util.listSongs())


def playSong(controller: ProController, queue: Queue, songName: str, generatorName: str):
    import generators
    import librosa

    D, y, sr, file = None, None, None, None
    try:
        y, sr, file = util.loadSongFromMp3(songName)
        D = librosa.stft(y[0], n_fft=2048)
    except Exception as e:
        print(e)
        return False

    g = {
        "RGBGenerator": generators.RGBGenerator,
        "WaveGenerator": generators.WaveGenerator
    }

    if generatorName not in g.keys():
        print("Invalid generator name. Valid generators are:", list(g.keys()))
        return False
    generator = g[generatorName](NUM_PIXELS, D, sr)

    print("Playing:", songName)

    mixer = util.playSong(file)
    time.sleep(0.2)

    start = time.time()
    songDuration = util.getTimes(D, sr)[-1]

    lastMessage = ProcessMessage()
    while time.time() - start < songDuration + 1 and not lastMessage.stop:
        if not queue.empty():
            lastMessage = queue.get_nowait()

        t = time.time() - start
        i = util.timeToBin(t, D, sr)

        c = generator.sample(t)
        controller.set(c)
        controller.write()

        time.sleep(0.01)

    if lastMessage.stop:
        mixer.music.stop()
        print("Song stopped")
    else:
        print("Song finished")
    return True


def setColor(controller: ProController, queue: Queue, R: int, G: int, B: int):
    R = int(R)
    G = int(G)
    B = int(B)
    if 0 <= R <= 255 and 0 <= G <= 255 and 0 <= B <= 255:
        print("Setting color: (" + str(R), str(G), str(B) + ")")
        for i in range(controller.numPixels):
            controller.set_pixel(i, R, G, B)
        controller.write()


def clear(controller: ProController, queue: Queue):
    controller.clear()
    controller.write()


commands = {
    "setColor": setColor,
    "clear": clear,
    "sunClock": sunClock,
    "oceanWave": oceanWave,
    "rainbow": rainbow,
    "playSong": playSong,
    "listSongs": listSongs,
}


def main():
    ports = []
    portNum = None
    for i, port in enumerate(serial.tools.list_ports.comports()):
        ports.append(port)
        print("[" + str(i) + "]: " + str(port.name))
    while portNum is None:
        try:
            n = int(input("Port number: "))
            if n > len(ports) or n < 0:
                print("Invalid port number")
            else:
                portNum = n
        except Exception as e:
            print(e)

    controller = ProController(NUM_PIXELS, os.path.join("/dev", ports[portNum].name))

    class DrlmProcess:
        pass

    currProcess = None
    currProcessQueue = None

    end = False
    # threads are keys and values are queues for each thread
    while not end:
        cmd = input(">>> ").strip().split(" ")

        if cmd == ['']:
            continue

        # Check if process is still alive, if it is not forget about it
        if currProcess is not None and not currProcess.is_alive():
            currProcess = None
            currProcessQueue = None

        # Process commands
        if cmd[0] == "exit":
            end = True
        elif cmd[0] == "stop":
            if currProcess is not None:
                stopMessage = ProcessMessage(stop=True)
                currProcessQueue.put(stopMessage)
                currProcess.join()
            else:
                print("No processes to stop")
        elif cmd[0] in commands.keys():
            try:
                if currProcess is None:
                    q = Queue()
                    currProcess = threading.Thread(target=commands[cmd[0]], args=(controller, q, *cmd[1:]))
                    currProcessQueue = q
                    currProcess.start()
                else:
                    print("A process is currently running, please stop the current process before starting a new one")
            except Exception as e:
                print(e)
        else:
            print("Invalid command!")
            print(list(commands.keys()))


if __name__ == "__main__":
    main()

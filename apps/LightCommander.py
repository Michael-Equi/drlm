from __future__ import unicode_literals
import time
import multiprocessing as mp
import youtube_dl
import os
import re

from drlm_common.datatypes import Color
from SolidColorApp import SolidColor
from music.MusicApp import MusicApp

# Helper function for making every string in a list lower case
def lowerArgs(args):
    return [arg.lower() for arg in args]

class LightCommander:

    def __init__(self):
        # Can only be running one process at a time
        self.process = None

    def _startMP(self, app, args=()):
        if self.process is None:
            self.process = mp.Process(target=app.run, args=args)
            self.process.start()
            return True
        else:
            return False

    def _stopMP(self):
        if self.process is not None:
            if self.process.is_alive():
                self.process.terminate()
            self.process = None
            return True
        return False

    """
    run functions handle args and run the desired app
    """

    def _runReadingLight(self, args):
        brightness = 1
        if len(args) > 0:
            brightness = abs(float(args[0]))
        r = min(255, int(15 * brightness))
        g = min(255, int(7 * brightness))
        b = min(255, int(1 * brightness))
        return self._startMP(SolidColor(Color.from_rgb(r, g, b), [(150, 250)]))

    def _runStripLighting(self, args):
        # args are r g b start1 end1 start2 end2 start3 end3  ...
        r = min(255, int(args[0]))
        g = min(255, int(args[1]))
        b = min(255, int(args[2]))
        if len(args) == 3:
            ranges = []
        else:
            rgs = args[3:]
            ranges = [(int(rgs[2*i]), int(rgs[2*i + 1])) for i in  range(len(rgs) // 2)]
        return self._startMP(SolidColor(Color.from_rgb(r, g, b), ranges))

    def _runMusic(self, args):
        # Make everything lower case so it is not case sensitive
        args = lowerArgs(args)
        app = MusicApp()
        # Need to map lower case song and generator names to actual names
        songs = app.getSongNames()
        generators = app.getGeneratorNames()
        generatorsLower = [g.lower() for g in generators]
        songsLower = [s.lower() for s in songs]
        song = args[0]
        if len(args) == 2:
            generator = args[1]
        else:
            generator = app.getGeneratorNames()[-1].lower()
        print(song, song + ".mp3" in songsLower, generator in generatorsLower)
        if song + ".mp3" in songsLower and generator in generatorsLower:
            song = songs[songsLower.index(song + ".mp3")].replace(".mp3", "")
            print(song)
            generator = generators[generatorsLower.index(generator)]
            print(generator)
            return self._startMP(app, (song, generator))
        return False

    def _getSongs(self):
        app = MusicApp()
        return [s.replace(".mp3", "") for s in app.getSongNames()]

    def _getGenerators(self):
        app = MusicApp()
        return app.getGeneratorNames()

    def _runLoadSong(self, args):
        # These args need to be case sensitive
        # Remove all existing mp3s in the file
        for f in filter(lambda x: ".mp3" in x, os.listdir()):
            os.remove(f)

        # Make sure name is valid
        name = args[1]
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~: .-]')
        if regex.search(name) is not None:
            raise Exception("Invald name")

        link = args[0]
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # Move mp3 to proper location with correct name
        f = list(filter(lambda x: ".mp3" in x, os.listdir()))[0]
        dest = os.path.join(os.environ["MUSIC_PATH"], name + ".mp3")
        os.rename(f, dest)
        print(f"File moved to {dest}")
        return True

    """
    Handle message function is the primary interface used by external
    applications
    """
    def handleMessage(self, msg):
        try:
            status = False
            args = msg.split(" ")
            cmds = {"reading-light": self._runReadingLight,
                    "strip-light": self._runStripLighting,
                    "play-song": self._runMusic,
                    "load-song": self._runLoadSong,
                    "kill": lambda _: self._stopMP()}
            """
            Special commands
            """
            cmd = args[0].lower()
            special_commands = ['ls-songs', 'ls-generators']
            if cmd == "ls":
                return f"Available commands: {list(cmds.keys()) + special_commands}\n"
            if cmd == "ls-songs":
                return f"Available songs: {self._getSongs()}\n"
            if cmd == "ls-generators":
                return f"Available generators: {self._getGenerators()}\n"

            """
            General commands
            """
            if cmd in cmds.keys():
                status = cmds[cmd](args[1:])

            return f"Executed {msg} with status {('SUCCESS' if status else 'ERROR')}\n"
        except Exception as e:
            return f"Failed with exception: {e}\n"

def main():
    # lc = LightCommander()
    # print(lc.handleMessage("load-song https://www.youtube.com/watch?v=hkNl3pq1twE IWouldDie4U"))
    # time.sleep(100)
    print(lc.handleMessage("ls-songs"))
    print(lc.handleMessage("play-song TheCranberriesDreams"))
    time.sleep(50)
    # print(lc.handleMessage("kill"))
    # print(lc.handleMessage("ls"))
    # print(lc.handleMessage("reading-light"))
    # time.sleep(5)
    # print(lc.handleMessage("kill"))
    # time.sleep(5)
    # print(lc.handleMessage("strip-light 155 32 189 10 20 70 80 250 300"))
    # time.sleep(5)
    # print(lc.handleMessage("kill"))

if __name__ == "__main__":
    main()

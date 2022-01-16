import time
import multiprocessing as mp

from drlm_common.datatypes import Color
from SolidColorApp import SolidColor
from music.MusicApp import MusicApp

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

    """
    Handle message function is the primary interface used by external
    applications
    """
    def handleMessage(self, msg):
        try:
            status = False
            args = msg.lower().split(" ")
            cmds = {"reading-light": self._runReadingLight,
                    "strip-light": self._runStripLighting,
                    "play-song": self._runMusic,
                    "kill": lambda _: self._stopMP()}
            """
            Special commands
            """
            special_commands = ['ls-songs', 'ls-generators']
            if args[0] == "ls":
                return f"Available commands: {list(cmds.keys()) + special_commands}\n"
            if args[0] == "ls-songs":
                return f"Available songs: {self._getSongs()}\n"
            if args[0] == "ls-generators":
                return f"Available generators: {self._getGenerators()}\n"

            """
            General commands
            """
            if args[0] in cmds.keys():
                status = cmds[args[0]](args[1:])

            return f"Executed {msg} with status {('SUCCESS' if status else 'ERROR')}\n"
        except Exception as e:
            return f"Failed with exception: {e}\n"

def main():
    lc = LightCommander()
    print(lc.handleMessage("ls-songs"))
    print(lc.handleMessage("play-song TheCranberriesDreams"))
    time.sleep(50)
    print(lc.handleMessage("kill"))
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

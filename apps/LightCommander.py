import time
import multiprocessing as mp

from drlm_common.datatypes import Color
from SolidColorApp import SolidColor

class LightCommander:

    def __init__(self):
        # Can only be running one process at a time
        self.process = None

    def _startMP(self, app):
        if self.process is None:
            self.process = mp.Process(target=app.run, args=())
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
                    "kill": lambda _: self._stopMP()}
            if args[0] == "ls":
                return f"Available commands: {list(cmds.keys())}\n"
            if args[0] in cmds.keys():
                status = cmds[args[0]](args[1:])
            return f"Executed {msg} with status {('SUCCESS' if status else 'ERROR')}\n"
        except Exception as e:
            return f"Failed with exception: {e}\n"

def main():
    lc = LightCommander()
    print(lc.handleMessage("ls"))
    print(lc.handleMessage("reading-light"))
    time.sleep(5)
    print(lc.handleMessage("kill"))
    time.sleep(5)
    print(lc.handleMessage("strip-light 155 32 189 10 20 70 80 250 300"))
    time.sleep(5)
    print(lc.handleMessage("kill"))

if __name__ == "__main__":
    main()

import time
from random import randint

from drlm_common.datatypes import Color
from drlm_controllers.drlm_controller import DrlmSimController

if __name__ == "__main__":
    controller = DrlmSimController(288)
    while True:
        controller.write()
        for i in range(288):
            controller.set_pixel(i, Color.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255)))
        time.sleep(0.1)

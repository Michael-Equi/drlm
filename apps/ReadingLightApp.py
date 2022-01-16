import time

from drlm_app.drlm_app import DrlmApp
from drlm_common.datatypes import Color
from SolidColorApp import SolidColor

if __name__ == "__main__":
    app = SolidColor(Color.from_rgb(15, 7, 1), ranges = [(150, 250)])
    app.run()
    app.close()

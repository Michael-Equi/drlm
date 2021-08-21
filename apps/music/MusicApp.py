import time

import generators
import librosa
import utils

from drlm_app.drlm_app import DrlmApp


class MusicApp(DrlmApp):
    def __init__(self, speed=10000, offset=0.2, host: str = 'localhost', port: int = 5555):
        super().__init__(host, port)
        self.speed = speed
        self.offset = offset

    def run(self):

        # song_name = input("Enter song name")
        # generator_name = input("Enter generator name")

        song_name = "SuperTrouper"
        generator_name = "PulseGenerator"

        D, y, sr, file = None, None, None, None
        try:
            y, sr, file = utils.load_song_from_mp3(song_name)
            D = librosa.stft(y[0], n_fft=2048)
        except Exception as e:
            print(e)
            return False

        g = {
            "RGBGenerator": generators.RGBGenerator,
            "WaveGenerator": generators.WaveGenerator,
            "PulseGenerator": generators.PulseGenerator
        }

        if generator_name not in g.keys():
            print("Invalid generator name. Valid generators are:", list(g.keys()))
            return False
        generator = g[generator_name](self.num_leds, D, sr)

        print("Playing:", song_name)

        utils.play_song(file)
        time.sleep(self.offset)

        start = time.time()
        song_duration = utils.get_times(D, sr)[-1]

        while time.time() - start < song_duration + 1:
            t = time.time() - start

            c = generator.sample(t)
            self.strip.set(c)
            self.write()

            time.sleep(1/self.speed)

        print('Song Finished')
        return True


if __name__ == "__main__":
    app = MusicApp()
    app.run()
    app.close()

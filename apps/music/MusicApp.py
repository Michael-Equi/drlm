import time
import os
from pathlib import Path

import apps.music.generators as generators
import librosa
import apps.music.utils as utils

from drlm_app.drlm_app import DrlmApp

"""
Make sure to set the MUSIC_PATH environment variable before running
eg: export MUSIC_PATH=/Users/michaelequi/Github/drlm/apps/music/music
"""

def pretty_print_list(li):
    li = list(li)
    items_per_line = 3
    line_length = max(map(lambda x: len(x), li)) + 3

    print("---")
    s = ""
    ct = 0
    for item in li:
        s += f"{item} {' ' * (line_length - len(item))}"
        ct += 1
        if ct == items_per_line:
            s += "\n"
            ct = 0
    print(s)
    print("---\n")

class MusicApp(DrlmApp):
    def __init__(self, speed=2000, offset=0, host: str = 'localhost', port: int = 5555):
        super().__init__(host, port)
        self.speed = speed
        self.offset = offset

        self.g = {
            "RGBGenerator": generators.RGBGenerator,
            "WaveGenerator": generators.WaveGenerator,
            "PulseGenerator": generators.PulseGenerator,
            "CenteredPulseGenerator": generators.CenteredPulseGenerator
        }

    def getSongNames(self):
        available_songs = utils.list_songs(path=Path(os.environ['MUSIC_PATH']))
        return available_songs

    def getGeneratorNames(self):
        return list(self.g.keys())

    def run(self, song_name, generator_name):
        try:
            D, y, sr, file = None, None, None, None
            try:
                y, sr, file = utils.load_song_from_mp3(song_name, path=Path(os.environ['MUSIC_PATH']))
                D = librosa.stft(y[0], n_fft=2048)
            except Exception as e:
                print(e)
                return False

            tempo = librosa.beat.tempo(y[0], sr)[0]

            generator = self.g[generator_name](self.num_leds, D, sr)

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

                # time.sleep(1 / self.speed)
                time.sleep(1 / (tempo / 60 * (self.num_leds / 2)))

            print('Song Finished\n\n')
        except KeyboardInterrupt:
            return True

class Player:
    def __init__(self):
        self.music_app = MusicApp()


    def run(self):
        try:
            while True:
                available_songs = self.music_app.getSongNames()
                print("\nSongs: ")
                pretty_print_list(map(lambda x: x[:-4], available_songs))
                song_name = None
                while song_name is None:
                    song_name = input("Enter song name: ")
                    if song_name not in map(lambda x: x[:-4], available_songs):
                        print(song_name, "not found")
                        song_name = None
                    else:
                        print()

                print("Generators: ")
                generator_names = self.music_app.getGeneratorNames()
                pretty_print_list(generator_names)
                generator_name = None
                while generator_name is None:
                    generator_name = input("Enter generator name (default - CenteredPulseGenerator): ")
                    if generator_name == "":
                        generator_name = "CenteredPulseGenerator"
                    if generator_name not in generator_names:
                        print(generator_name, "not found")
                        generator_name = None
                    else:
                        print()

                self.music_app.run(song_name, generator_name)
        except KeyboardInterrupt:
            return True

    def close(self):
        self.music_app.close()


if __name__ == "__main__":
    player = Player()
    player.run()
    player.close()

from pygame import mixer
import time


def main():
    mixer.init()
    mixer.music.load('music/GentleEarthquakes.mp3')
    mixer.music.play()

    time.sleep(5)

    print("Pausing")
    mixer.music.pause()

    time.sleep(2)

    print("Unpause")
    mixer.music.unpause()

    time.sleep(5)



if __name__ == "__main__":
    main()

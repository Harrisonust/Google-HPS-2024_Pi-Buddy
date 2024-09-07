import audioop
import time


import pyaudio
from typing import List


class settings:
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    NUM_SAMPLES = 1024

    HISTLEN = 256
    SAMPLELEN = 128

    TICK = 0.01


# history: List[int] = []


# p = pyaudio.PyAudio()
# stream = p.open(
#     format=pyaudio.paInt16,
#     channels=settings.CHANNELS,
#     rate=settings.RATE,
#     frames_per_buffer=settings.NUM_SAMPLES,
#     input=True,
# )



# while True:
#     available = 0
#     while True:
#         available = stream.get_read_available()
#         if available >= settings.NUM_SAMPLES:
#             break

#         time.sleep(settings.TICK)

#     data = stream.read(available)[-settings.NUM_SAMPLES:]
#     rms = audioop.rms(data, 2)

#     # Store and recalculate mean
#     if len(history) >= settings.HISTLEN:
#         history.pop(0)
#     history.append(rms)
#     history_mean = sum(history) / len(history)

#     # Calculate sample
#     sample = history[-settings.SAMPLELEN :]
#     sample_mean = sum(sample) / len(sample)

#     if history_mean:
#         derivation = sample_mean / history_mean / 100
#     else:
#         derivation = 0

#     msg = "sample: %.03f\tmean: %.03f\tderivation: %.04f"
#     msg = msg % (sample_mean, history_mean, derivation)
#     print(msg, end="\r", flush=True)


class SoundDetector:

    def __init__(self, setttings):
        self.settings = settings

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.settings.FORMAT,
            channels=self.settings.CHANNELS,
            rate=self.settings.RATE,
            frames_per_buffer=self.settings.NUM_SAMPLES,
            input=True,
        )

        self.buffer = []

    def get_volume(self):
        available = 0
        while True:
            available = self.stream.get_read_available()
            if available >= self.settings.NUM_SAMPLES:
                break

            time.sleep(self.settings.TICK)

        data = self.stream.read(available)[-settings.NUM_SAMPLES:]
        rms = audioop.rms(data, 2)

        return rms

    def calculate_silence(self, seconds=5):
        buff = []
        start = time.time()
        blocks = int(self.settings.RATE / self.settings.NUM_SAMPLES )
        while len(buff) < blocks:
            buff.append(self.get_volume())
        print('time', time.time() - start)
        return sum(buff) / len(buff)

    def watch(self, silence, seconds=5):
        blocks = int(self.settings.RATE / self.settings.NUM_SAMPLES * seconds)
        history = []

        in_silence = True

        while True:
            level = self.get_volume()
            if len(history) >= blocks:
                history.pop(0)
            history.append(level)

            mean = sum(history) / blocks
            if (mean > silence and in_silence):
                print("Sound!")
                in_silence = False

            elif (mean < silence and not in_silence):
                print("Silence!")
                in_silence = True


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--silence", dest="silence", type=int, default=0)
    parser.add_argument("-w", "--watch", dest="watch", action='store_true')
    args = parser.parse_args()

    sd = SoundDetector(settings)

    if args.silence == 0:
        print("Calculating value for silence...\r", end='', flush=True)
        args.silence = sd.calculate_silence() * 0.9
        print("Silence level: %.04f kk " % args.silence)

    if args.watch:
        sd.watch(silence=args.silence)
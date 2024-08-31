import pyaudio
import wave
import sys

from respeaker_defines import *

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(rate=SAMPLE_RATE,
                    format=p.get_format_from_width(DATA_WIDTH),
                    channels=MIC_CHANNEL_NUM,
                    output=True,
                    output_device_index=DEVICE_INDEX)

    while 1:
        stream.write(data)

    stream.close()
    p.terminate()



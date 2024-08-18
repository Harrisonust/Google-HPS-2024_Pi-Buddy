import pyaudio
import wave

from respeaker_defines import *

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(rate=SAMPLE_RATE,
                    format=p.get_format_from_width(DATA_WIDTH),
                    channels=MIC_CHANNEL_NUM,
                    input=True,
                    input_device_index=DEVICE_INDEX,)

    while 1:
        data = stream.read(DATA_CHUNK_SIZE)
    
    stream.stop_stream()
    stream.close()
    p.terminate()

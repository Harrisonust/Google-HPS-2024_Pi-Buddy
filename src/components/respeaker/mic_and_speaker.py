import pyaudio
import wave
import time

from respeaker_defines import *

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(rate=SAMPLE_RATE,
                    format=p.get_format_from_width(DATA_WIDTH),
                    channels=MIC_CHANNEL_NUM,
                    input=True,
                    input_device_index=DEVICE_INDEX,
                    output=True,
                    output_device_index=DEVICE_INDEX,)

    start = time.time()
    dataframe = None
    data = []

    while 1:
        if time.time() - start < 5.0:
            print('recording')
            dataframe = stream.read(DATA_CHUNK_SIZE)
            data.append(dataframe)
        else:
            print('playing')
            for dataframe in data: 
                stream.write(dataframe)
            break
    
    stream.stop_stream()
    stream.close()
    p.terminate()

from picamera2 import Picamera2, Preview
from libcamera import Transform

from PIL import Image

if __name__ == '__main__':
    picam2 = Picamera2()
    
    # option 1: a high level way to capture and save as file
    # picam2.start_preview(Preview.NULL)
    # picam2.start_and_capture_file("test.jpg")
    
    # option 2: capture as a numpy array
    picam2.start()
    frame = picam2.capture_array()

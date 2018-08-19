import numpy as np
from PIL import ImageGrab, Image
from mss.windows import MSS as mss
import mss.tools as tools
from time import time
import cv2
import random


def get_screen(sct, monitor):
    screenshot = sct.grab(monitor)
    return np.asarray(
        Image.frombytes(
            'RGB',
            screenshot.size,
            screenshot.bgra,
            'raw',
            'BGRX'
        )
        #.tobytes()
    )

def noise_screen(monitor):
    return np.array(
        np.random.random_integers(
            0,
            255,
            (
                monitor['height'] - monitor['top'],
                monitor['width'] - monitor['left'],
                3
            )
        ),
        dtype=np.uint8
    )

def save_noise_video(monitor, seconds):
    noise_screens = []
    for i in range(0,100):
        noise_screens.append(noise_screen(monitor=monitor))
        
    writer = cv2.VideoWriter('testvid.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 30, (monitor['width'], monitor['height']), True)
    for i in range(0, 30*seconds):
        writer.write(noise_screens[random.randint(0,99)])
    writer.release()



# Youtube video
monitor = {'top': 165, 'left': 205, 'width': 1200, 'height': 700}
writer = cv2.VideoWriter(
    filename='testvid.avi',
    fourcc=cv2.VideoWriter_fourcc('M','J','P','G'),
    fps=30,
    frameSize=(monitor['width'], monitor['height']),
    isColor=True
)

with mss() as sct:
    for i in range(0, 32*20):
        writer.write(get_screen(sct=sct, monitor=monitor))

#with mss() as sct:
#    for i in range(0,100):
#        writer.write(get_screen(sct=sct, monitor={'top': 0, 'left': 0, 'width': 640, 'height': 360}))

#with mss() as sct:
#    np.asarray(get_screen(sct=sct, monitor={'top': 0, 'left': 0, 'width': 1280, 'height': 960}))



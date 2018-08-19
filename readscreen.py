import numpy as np
from PIL import ImageGrab, Image
from mss.windows import MSS as mss
import mss.tools as tools
import time
import cv2
import random
import math

def get_screen(sct, monitor):
    """
    Grabs screenshot using sct and pillow
    """
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
    """
    Makes colored noise screenshot with given dimensions.
    """
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

def save_noise_video(monitor, fps, seconds):
    """
    Saves video with noise as frames.
    """
    noise_screens = []
    for i in range(0,100):
        noise_screens.append(noise_screen(monitor=monitor))
        
    writer = cv2.VideoWriter('testvid.avi', cv2.VideoWriter_fourcc('M','J','P','G'), fps, (monitor['width'], monitor['height']), True)
    for i in range(0, fps*seconds):
        writer.write(noise_screens[random.randint(0,99)])
    writer.release()


def make_recording(monitor, seconds):
    images = []
    start_time = time.time()
    with mss() as sct:
        while time.time() - start_time < seconds:
            images.append({
                'image': get_screen(sct=sct, monitor=monitor),
                'time': time.time()
            })
    return images
    

def write_recording(images, fps):
    """
    Converts recorded array of images to video avi format.
    Resulting video is in given fps.
    If given recording has missing frames, they are filled with the previous frame.
    """
    
    writer = cv2.VideoWriter(
        filename='testvid.avi',
        fourcc=cv2.VideoWriter_fourcc('M','J','P','G'),
        fps=fps,
        frameSize=(monitor['width'], monitor['height']),
        isColor=True
    )
    # Write first image, then iterate from there
    writer.write(images[0]['image'])
    start_time = images[0]['time']
    image_idx_prev = 0
    image_idx_current = 1
    # Loop over each frame of resulting video, if recording (images) is missing frames then fill it in with the most recent frame
    for frame_count in range(1, fps*seconds):

        # Take next image when the realtime video has reached the time of that image
        # parse frame_count into seconds and the remaining fractions of the second (fps)
        target_image_time = start_time + math.floor(frame_count / fps) + (frame_count % fps) / fps
        
        # Try increment to next image if realtime video's frame time is past next image's time
        if image_idx_current + 1 < len(images) and target_image_time >= images[image_idx_current]['time']:
            image_idx_current += 1
            image_idx_prev += 1

        # Write current image to video (if no increment then write same image again)
        writer.write(images[image_idx_current]['image'])


        
fps = 30
seconds = 5

monitor = {'top': 0, 'left': 0, 'width': 1400, 'height': 900}
images = make_recording(monitor=monitor, seconds=seconds)
write_recording(images=images, fps=fps)


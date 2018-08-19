import numpy as np
from PIL import ImageGrab, Image
from mss.windows import MSS as mss
import mss.tools as tools
import time
import cv2
import random
import math
import sys
import json
import multiprocessing as mp

def get_screen(sct, monitor):
    """
    Grab screenshot without processing it, for faster capture
    """
    return sct.grab(monitor)

def process_screen(screen):
    #return np.reshape(image, (size.width, size.height, 3))
    return np.asarray(
        Image.frombytes(
            'RGB',
            screen.size,
            screen.bgra,
            'raw',
            'BGRX'
        )
        #.tobytes()
    )

def analyze_recording(recording):
    """
    Analyzes recording from file and reports its quality.
    """
    biggest_framedrop = 0
    frame_prev = None
    for frame in recording:
        if frame_prev is not None:
            biggest_framedrop = max(biggest_framedrop, frame[0][0] - frame_prev[0][0])
        frame_prev = frame
    frames = len(recording)
    duration = recording[len(recording)-1][0][0] - recording[0][0][0]
    return {
        'duration': duration,
        'frames': frames,
        'average_fps': -1 if duration == 0 else frames/duration,
        'biggest_framedrop': biggest_framedrop
    }
    
def make_recording(monitor, seconds):
    print('Start recording')
    start_time = time.time()
    recording = None
    with mss() as sct:
        while time.time() - start_time < seconds:
        
            # todo deze terug naar rgb toe, geen grijstinten meer
            # Record screen
            pixels = cv2.cvtColor(
                np.array(
                    ImageGrab.grab(
                        bbox=(monitor['top'], monitor['left'], monitor['height'], monitor['width'])
                    )
                ),
                cv2.COLOR_BGR2GRAY
            )
            frame = np.array([
                [time.time()],
                np.swapaxes(pixels, 0, 1)
            ])
            
            
            # Append screen to recording
            if recording is None:
                recording = np.array([frame])
            else:
                recording = np.concatenate((recording, np.array([frame])))
    
    print('Stop recording')
    return recording
    
def RGBify_recording(recording):
"""
Fills in rgb values for grayscale pixels (1 int to 3 ints)
"""
    
    def RGBify_image(image):
        new_image = np.zeros((len(image), len(image[0]), 3), dtype='uint8')
        for x in range(0, len(image)):
            for y in range(0, len(image[0])):
                for z in range(0, 3):
                    new_image[x][y][z] = image[x][y]
        return new_image
    
    recording2 = None
    count = 0
    for image in recording:
        print('{}/{}'.format(count, len(recording)))
        count+=1
        if recording2 is None:
            recording2 = np.array([np.array([image[0], RGBify_image(image[1])])])
        else:
            recording2 = np.concatenate((recording2, np.array([np.array([image[0], RGBify_image(image[1])])])))
    return recording2

def convert_recording_to_video(recording, monitor, fps):
    """
    Converts recorded array of images to video avi format.
    Resulting video is in given fps.
    If given recording has missing frames, they are filled with the previous frame.
    Recording must be [r,g,b] per pixel.
    """
    
    
    writer = cv2.VideoWriter(
        filename='testvid.avi',
        fourcc=cv2.VideoWriter_fourcc('M','J','P','G'),
        fps=fps,
        frameSize=(monitor['width'], monitor['height']),
        isColor=True
    )
    
    image_idx = 0
    writer.write(recording[image_idx][1]) # Write first image, then iterate from there
    start_time = recording[0][0][0]
    # Loop over each frame of resulting video, if recording (recording) is missing frames then fill it in with the most recent frame
    for frame_count in range(1, fps*seconds):

        # Take next image when the realtime video has reached the time of that image
        # parse frame_count into seconds and the remaining fractions of the second (fps)
        target_image_time = start_time + math.floor(frame_count / fps) + (frame_count % fps) / fps
        
        # Try increment to next image if realtime video's frame time is equal to or past next image's time
        if image_idx + 1 < len(recording) and target_image_time >= recording[image_idx][0][0]:
            image_idx += 1

        # Write current image to video (if no increment then write same image again)
        writer.write(recording[image_idx][1])
    writer.release()

if __name__ == '__main__':  

    fps = 30
    seconds = 1

    monitor = {'top': 0, 'left': 0, 'width': 1400, 'height': 900}
    recording = make_recording(monitor=monitor, seconds=seconds)
    print(analyze_recording(recording=recording))
    recording_rgb = RGBify_recording(recording=recording)
    np.save('recording_rgb.npy', recording_rgb)
    recording_rgb = np.load('recording_rgb.npy')
    convert_recording_to_video(recording=recording_rgb, monitor=monitor, fps=fps)
    


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

def analyze_recording(filename):
    """
    Analyzes recording from file and reports its quality.
    """
    with open(filename, 'r') as file:
        recording = []
        while True:
            row = file.readline()
            if row is None or row == '':
                break;
            recording.append(json.loads(row))
        
        biggest_framedrop = 0
        frame_prev = None
        for frame in recording:
            if frame_prev is not None:
                biggest_framedrop = max(biggest_framedrop, frame['time'] - frame_prev['time'])
            frame_prev = frame
        frames = len(recording)
        duration = recording[len(recording)-1]['time'] - recording[0]['time']
        return {
            'duration': duration,
            'frames': frames,
            'average_fps': -1 if duration == 0 else frames/duration,
            'biggest_framedrop': biggest_framedrop
        }

    
def parallel_file_write_recording(params):
    filename, recording_chunk = params[0], params[1]
    print('parallel writing chunksize={}'.format(len(recording_chunk)))
    write_string = ''
    for frame in recording_chunk:
        
        # Stringify
        write_string += json.dumps({'time': frame['time'], 'image': frame['image'].tolist()}).replace(' ', '') + '\n'
        
    # Write
    with open(filename, 'a') as file:
        file.write(write_string)
    
    print('parallel done')
    
def make_recording(filename, monitor, seconds):
    pool = mp.Pool(processes=3)
    processes = []
    start_time = time.time()
    recording_chunk = []
    first_write = True
    print('Start recording')
    
    # Clear file
    with open(filename, 'w') as file:
        file.write('')
        
    with mss() as sct:
        while time.time() - start_time < seconds:
            # Record screen and put it into chunk
            recording_chunk.append({
                'time': time.time(),
                'image': cv2.cvtColor(np.array(ImageGrab.grab(bbox=(monitor['top'], monitor['left'], monitor['height'], monitor['width']))), cv2.COLOR_BGR2GRAY)
            })
            # If chunk is big enough: async write to file with multiprocessing pool.
            if len(recording_chunk) >= 30:
                processes.append(
                    pool.map_async(
                        parallel_file_write_recording,
                        [[filename, recording_chunk]]
                    )
                )
                recording_chunk = []
                first_write = False
    for p in processes:
        p.get()
    print('Stop recording')

def convert_recording_to_video(filename, fps):
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
    writer.write(recording[0]['image'])
    start_time = recording[0]['time']
    image_idx_prev = 0
    image_idx_current = 1
    # Loop over each frame of resulting video, if recording (recording) is missing frames then fill it in with the most recent frame
    for frame_count in range(1, fps*seconds):

        # Take next image when the realtime video has reached the time of that image
        # parse frame_count into seconds and the remaining fractions of the second (fps)
        target_image_time = start_time + math.floor(frame_count / fps) + (frame_count % fps) / fps
        
        # Try increment to next image if realtime video's frame time is past next image's time
        if image_idx_current + 1 < len(recording) and target_image_time >= recording[image_idx_current]['time']:
            image_idx_current += 1
            image_idx_prev += 1

        # Write current image to video (if no increment then write same image again)
        writer.write(recording[image_idx_current]['image'])




# define a example function
def rand_string(length, output):
    """ Generates a random string of numbers, lower- and uppercase chars. """
    rand_str = ''.join(random.choice(
                        string.ascii_lowercase
                        + string.ascii_uppercase
                        + string.digits)
                   for i in range(length))
    output.put(rand_str)

import string

if __name__ == '__main__':  

    fps = 30
    seconds = 5

    monitor = {'top': 0, 'left': 0, 'width': 1400, 'height': 900}
    make_recording(filename='recording', monitor=monitor, seconds=seconds)
    print(analyze_recording(filename='recording'))
    #convert_recording_to_video(recording=recording, fps=fps)
    


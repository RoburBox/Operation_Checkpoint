import numpy as np
from PIL import ImageGrab, Image
from mss.windows import MSS as mss
import time
import cv2
import math
import psutil
import os
import datetime
from pynput.keyboard import Key, Listener
import multiprocessing
import ctypes
import myModule

def get_screen(sct, monitor):
    """
    Grab screenshot without processing it, for faster capture
    """
    return sct.grab(monitor)

def process_screen(screen):
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

def analyze_recording(folder_path):
    """
    Analyzes recording from file and reports its quality.
    """
    biggest_framedrop = 0
    keys_pressed = 0
    frame_prev = None
    file_names = sorted(os.listdir(folder_path), key=lambda file_name: int(file_name.split('frame_')[1].split('.npy')[0]))
    for file_name in file_names:
        frame = np.load('{}{}'.format(folder_path, file_name))
        if frame_prev is not None:
            biggest_framedrop = max(biggest_framedrop, frame[0][0] - frame_prev[0][0])
        keys_pressed += frame[1][0] + frame[1][1] + frame[1][2] + frame[1][3]
        frame_prev = frame
    frame_count = len(file_names)
    duration = np.load('{}{}'.format(folder_path, file_names[len(file_names)-1]))[0][0] - np.load('{}{}'.format(folder_path, file_names[0]))[0][0]
    return {
        'duration': duration,
        'frame_count': frame_count,
        'average_fps': -1 if duration == 0 else frame_count/duration,
        'biggest_framedrop': biggest_framedrop,
        'total_key_presses': keys_pressed
    }
 
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

def make_recording_and_save(monitor, folder_path, shared_arr):
    print('Press q to start recording, press w to stop recording')
    
    def on_release(key):
        if 'char' in dir(key) and key.char == 'q':
            return False
            
    # Wait for q key to be pressed before recording
    with Listener(on_release=on_release) as listener:
        listener.join()
        print('Start recording')
        
        start_time = time.time()
        try:
            with mss() as sct:
                for frame_nr in range(0, 500):
                
                    # W key pressed
                    if shared_arr[4] == 1:
                        shared_arr[4] = 0
                        break
                    
                    # Record screen
                    frame = np.array([
                        [time.time()],
                        [shared_arr[0], shared_arr[1], shared_arr[2], shared_arr[3]],
                        get_screen(sct=sct, monitor=monitor)
                    ])
                    
                    # Write frame to file
                    np.save('{}\\frame_{}'.format(folder_path, frame_nr), frame)
            
            print('Stop recording')
        except MemoryError as e:
            print('MemoryError caught, process is using {}MB for {} frames'.format(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, frame_nr))
            raise e


def make_folder():
    if os.path.exists('data') == True:
        folder_path = 'data\\{}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H_%M_%S+0000'))
        os.makedirs(folder_path)
        return folder_path + '\\'
    else:
        raise Exception('Could not save recording, path does not exist')
    
    
def parallel_listen(param):
    """
    Runs key listener and keeps myModule.shared_arr up to date.
    The array contains, in order: keyup, keyright, keydown, keyleft, w
    The w key is only set to 1 and is expected to be set to 0 somewhere else.
    """
    def on_press(key):
        if key == Key.up:
            myModule.shared_arr[0] = 1
        elif key == Key.right:
            myModule.shared_arr[1] = 1
        elif key == Key.down:
            myModule.shared_arr[2] = 1
        elif key == Key.left:
            myModule.shared_arr[3] = 1
        elif 'char' in dir(key):
            if key.char == 'w':
                myModule.shared_arr[4] = 1
                return False
            
    def on_release(key):
        if key == Key.up:
            myModule.shared_arr[0] = 0
        elif key == Key.right:
            myModule.shared_arr[1] = 0
        elif key == Key.down:
            myModule.shared_arr[2] = 0
        elif key == Key.left:
            myModule.shared_arr[3] = 0
        # w is set by other process
        
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def initProcess(shared_arr):
  myModule.shared_arr = shared_arr

if __name__ == '__main__':
    monitor = {'top': 0, 'left': 0, 'width': 1280, 'height': 960}
    #folder_path = 'data\\2018-08-25T15_17_42+0000\\'
    
    # Share keyboard inputs with parallel key listener
    shared_arr = multiprocessing.Array('I', [0, 0, 0, 0, 0], lock=False)
    pool = multiprocessing.Pool(initializer=initProcess, processes=1, initargs=(shared_arr,))
    pool.map_async(parallel_listen, shared_arr)
    
    
    folder_path = make_folder()
    make_recording_and_save(monitor=monitor, folder_path=folder_path, shared_arr=shared_arr)
    
    print(analyze_recording(folder_path))
    #convert_recording_to_video(recording=recording_rgb, monitor=monitor, fps=fps)

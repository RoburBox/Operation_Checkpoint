import numpy as np
from PIL import ImageGrab
from mss.windows import MSS as mss
import time
import psutil
import os
import datetime
from pynput.keyboard import Key, Listener
import multiprocessing
import myModule
from process_recording import process_recording
from analyze_recording import analyze_recording

def get_screen(sct, monitor):
    """
    Grab screenshot without processing it, for faster capture
    """
    return sct.grab(monitor)

def make_recording_and_save(monitor, shared_arr):
    """
    Records and saves screenshots.
    Waits for key press to start and stop.
    """
    
    def on_release(key):
        if 'char' in dir(key) and key.char == 'a':
            return False
            
    print('Press a to start recording, press s to stop recording')
    with Listener(on_release=on_release) as listener:
        listener.join()
        print('Start recording')
        
        folder_path = make_folder()
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
            return folder_path
        except MemoryError as e:
            print('MemoryError caught, process is using {}MB for {} frames'.format(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, frame_nr))
            raise e


def make_folder():
    """
    Handles folder making and checking.
    Returns folder path string.
    """
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
            if key.char == 's':
                myModule.shared_arr[4] = 1
            
    def on_release(key):
        if key == Key.up:
            myModule.shared_arr[0] = 0
        elif key == Key.right:
            myModule.shared_arr[1] = 0
        elif key == Key.down:
            myModule.shared_arr[2] = 0
        elif key == Key.left:
            myModule.shared_arr[3] = 0
        # shared_arr[4] is set by other process
        
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def init_process(shared_arr):
    """
    Pool initializer
    """
    myModule.shared_arr = shared_arr

if __name__ == '__main__':
    monitor = {'top': 40, 'left': 10, 'width': 1280, 'height': 960}
    
    # Share keyboard inputs with parallel key listener
    shared_arr = multiprocessing.Array('I', [0, 0, 0, 0, 0], lock=False)
    pool = multiprocessing.Pool(initializer=init_process, processes=1, initargs=(shared_arr,))
    pool.map_async(parallel_listen, shared_arr)
    folder_path = make_recording_and_save(monitor=monitor, shared_arr=shared_arr)
    process_recording(folder_path)
    print(analyze_recording(folder_path))

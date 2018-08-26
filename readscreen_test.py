import numpy as np
import scipy.misc
from PIL import ImageGrab, Image
from mss.windows import MSS as mss
import mss.tools as tools
from time import time

def get_screen(bbox):
    return ImageGrab.grab(bbox=bbox)

def convert_arr(arr):
    """
    Converts 1d to 2d array
    """
    return np.array(arr).reshape((arr.size[1], arr.size[0], 3))

def arr_to_png(arr, location):
    """
    Can be 1d or 2d arr.
    """
    scipy.misc.imsave(location, arr)
    

def get_screen2(sct, monitor):
    screenshot = sct.grab(monitor)
    return Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX').tobytes() #convert from BGRA to RGB (mss docs zegt dat PIL versie snelste is?)


repeat=1000

start_time = time()
for i in range(0, repeat):
    get_screen((0,0, 1280, 960))
print('get_screen     x{} took {}'.format(repeat, time() - start_time))

start_time = time()
for i in range(0, repeat):
    convert_arr(get_screen((0,0, 1280, 960)))
print('get_screen np  x{} took {}'.format(repeat, time() - start_time))

with mss() as sct:
    start_time = time()
    for i in range(0, repeat):
        get_screen2(sct=sct, monitor={"top": 0, "left": 0, "width": 1280, "height": 960})
    print('get_screen2    x{} took {}'.format(repeat, time() - start_time))
    
    start_time = time()
    for i in range(0, repeat):
        np.asarray(get_screen2(sct=sct, monitor={"top": 0, "left": 0, "width": 1280, "height": 960}))
    print('get_screen2 np x{} took {}'.format(repeat, time() - start_time))






#arr_to_png(arr=screen1, location='test.png')
#print('Saving took {}'.format(str(np.asarray(screen2).shape)))
#start_time = time()
#output = 'test.png'
#tools.to_png(screen2.rgb, screen2.size, output=output)
#print('Saving took {}'.format(time() - start_time))
#print('Saved image: {}'.format(output))




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

def make_recording(monitor, seconds_max, frames_max):
    recording = None
    print('Start recording')
    start_time = time.time()
    max_frames = 340
    try:
        with mss() as sct:
            while recording is None or (len(recording) < max_frames and (frames_max is None or len(recording) < frames_max)):
                timenow = time.time()
                if seconds_max is not None and timenow - start_time >= seconds_max:
                    break
                    
                # Record screen
                frame = np.array([[timenow], get_screen(sct=sct, monitor=monitor)])
                
                # Append screen to recording
                if recording is None:
                    recording = np.array([frame])
                else:
                    recording = np.concatenate((recording, np.array([frame])))
        
        print('Stop recording')
        return recording
        
    except MemoryError as e:
        print('MemoryError caught, process is using {}MB for {} frames'.format(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, len(recording)))
        raise e


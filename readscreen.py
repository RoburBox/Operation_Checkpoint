import numpy as np
import scipy.misc
from PIL import ImageGrab, Image
from mss.windows import MSS as mss
import mss.tools as tools
from time import time

def get_screen(x_min, y_min, x_max, y_max):
    return ImageGrab.grab(bbox=(0,0, 1280, 960))

def convert_arr(arr):
    """
    Converts 1d to 2d array
    """
    return np.array(arr, dtype='uint8').reshape((arr.size[1], arr.size[0], 3))
    

def arr_to_png(arr, location):
    """
    Can be 1d or 2d arr.
    """
    scipy.misc.imsave(location, arr)
    



def get_screen2(monitor):
    # If converting this into function, remember to not instantiate a new mss() object each function call
    with mss() as sct:
        img = sct.grab(monitor)
        Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX').tobytes() #convert from BGRA ro RGB (mss docs zegt dat PIL versie snelste is?)
        return img



start_time = time()
arr_to_png(
    arr=get_screen(0, 0, 1280, 960),
    location='test.png'
)
print('arr_to_png took {}'.format(time() - start_time))


start_time = time()
img = get_screen2(monitor={"top": 0, "left": 0, "width": 1280, "height": 960})
print('get_screen2 took {}'.format(time() - start_time))
print('Saving took {}'.format(str(np.asarray(img).shape)))


start_time = time()
output = 'test.png'
tools.to_png(img.rgb, img.size, output=output)
print('Saving took {}'.format(time() - start_time))
print('Saved image: {}'.format(output))


import numpy as np
import scipy.misc
from PIL import ImageGrab

def get_screen(x_min, y_min, x_max, y_max):
    return ImageGrab.grab(bbox=(0,0, 1280, 960))

"""
Converts 1d to 2d array
"""
def convert_arr(arr):
    return np.array(arr, dtype='uint8').reshape((arr.size[1], arr.size[0], 3))
    
"""
Can be 1d or 2d arr.
"""
def arr_to_png(arr, location):
    scipy.misc.imsave(location, arr)
    
import time
start_time = time.time()
arr_to_png(
    arr=get_screen(0, 0, 1280, 960),
    location='test.png'
)
print('Took {}'.format(time.time() - start_time))

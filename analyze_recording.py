import os
import sys
import numpy as np
from asserts import assert_date_format

def analyze_recording(folder_path):
    """
    Analyzes recording from file and reports its quality.
    """
    print('Analyzing recording...')
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
    
if __name__ == '__main__':
    assert_date_format(sys.argv[1])
    print(analyze_recording('data\\{}\\'.format(sys.argv[1])))

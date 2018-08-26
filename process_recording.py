from PIL import Image
import os
import sys
from asserts import assert_date_format
import numpy as np

def process_frame(image):
    return np.asarray(
        Image.frombytes(
            'RGB',
            image.size,
            image.bgra,
            'raw',
            'BGRX'
        )
        #.tobytes()
    )
    
def process_recording(folder_path):
    file_names = sorted(os.listdir(folder_path), key=lambda file_name: int(file_name.split('frame_')[1].split('.npy')[0]))
    for (file_idx, file_name) in enumerate(file_names):
        print('Processing file {} of {}'.format(file_idx, len(file_names) - 1))
        file_path = '{}frame_{}.npy'.format(folder_path, file_idx)
        frame = np.load(file_path)
        frame[2] = process_frame(frame[2])
        np.save(file_path, frame)
    print('{} frames processed'.format(len(file_names)))
    
    
if __name__ == '__main__':
    assert_date_format(sys.argv[1])
    process_recording('data\\{}\\'.format(sys.argv[1]))

import cv2
import math
import ctypes
from PIL import Image
import sys
import os
import numpy as np


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

def convert_recording_to_video(folder_path, video_name, fps):
    """
    Converts recorded array of images to video avi format.
    Resulting video is in given fps.
    If recording has missing frames, they are filled with the previous frame.
    """
    
    
    def elapsed_seconds(frame_count, fps):
        """
        Returns number of seconds (float) at given frame number with given fps
        parse vid_frame_count into seconds and the remaining fractions of the second (fps)
        """
        return math.floor(vid_frame_count / fps) + ((vid_frame_count % fps) / fps)
    
    
    # Get all file names sorted
    file_names = sorted(os.listdir(folder_path), key=lambda file_name: int(file_name.split('frame_')[1].split('.npy')[0]))
    
    # Load file and process image
    frame = np.load('{}\\{}'.format(folder_path, file_names[0]))
    frame[2] = process_screen(frame[2])
    start_time = frame[0][0]
    
    print('Converting data files to video with dimensions w={} h={}'.format(len(frame[2][0]), len(frame[2])))
    writer = cv2.VideoWriter(
        filename=video_name,
        fourcc=cv2.VideoWriter_fourcc('M','J','P','G'),
        fps=fps,
        frameSize=(len(frame[2][0]), len(frame[2])),
        isColor=True
    )
    
    vid_frame_count = 1
    # Loop over each frame of resulting video, if recording (recording) is missing frames then fill it in with the most recent frame
    for (file_idx, file_name) in enumerate(file_names):
        print('Processing file {} of {}'.format(file_idx, len(file_names) - 1))
        
        if file_idx + 1 < len(file_names):
        
            # Load file and process image
            next_frame = np.load('{}\\{}'.format(folder_path, file_names[file_idx + 1]))
            next_frame[2] = process_screen(next_frame[2])
            
            # Keep writing this frame until it is time for next frame
            while start_time + elapsed_seconds(frame_count=vid_frame_count, fps=fps) < next_frame[0][0]:
                writer.write(frame[2])
                vid_frame_count += 1
                
            frame = next_frame
        else:
            # No next file, write remaining frames with last file
            writer.write(frame[2])
    writer.release()
    
if len(sys.argv) == 2:
    folder_name = sys.argv[1]

    # Verify command line arguments
    if not '\'' in folder_name:
        if len(folder_name.split('-')) == 3:
            if len(folder_name.split('T')) == 2:
                if len(folder_name.split('_')) == 3:
                    if len(folder_name.split('+')) == 2:

                        # Convert
                        convert_recording_to_video(
                            folder_path='data\\{}\\'.format(folder_name),
                            video_name='{}.avi'.format(folder_name),
                            fps=30
                        )
                    else:
                        print('Bad arguments: check 5 failed')
                else:
                    print('Bad arguments: check 4 failed')
            else:
                print('Bad arguments: check 3 failed')
        else:
            print('Bad arguments: check 2 failed')
    else:
        print('Bad arguments: check 1 failed')
else:
    print('Must give 1 argument')
print('Stopping...')


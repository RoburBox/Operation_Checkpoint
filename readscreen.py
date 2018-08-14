from mss.windows import MSS as mss
from time import time
from PIL import Image

import mss.tools as tools
import numpy as np


def main():
	start_time = time()
	
	# Define monitor range
	monitor = {"top": 0, "left": 0, "width": 1280, "height": 960}
	
	# If converting this into function, remember to not instantiate a new mss() object each function call
	with mss() as sct:
		img = sct.grab(monitor)
		Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX').tobytes() #convert from BGRA ro RGB (mss docs zegt dat PIL versie snelste is?) 
		
	print('\nCapturing took {}'.format(time() - start_time))
	print('Captured image array: ' + str(np.asarray(img).shape) + '\n')
	
	start_time = time()
	output = 'test.png'
	
	tools.to_png(img.rgb, img.size, output=output)
	
	print('Saving took {}'.format(time() - start_time))
	print('Saved image: ' + output + '\n')
	

# Als file in een module zit, zorgt deze check/constructie ervoor dat main code niet uitgevoerd wordt tijdens compilen	
if __name__ == "__main__":
	main()
	



import os
import glob
import numpy as np
from PIL import Image
from depth_map.log import logger

# Credit to: https://github.com/jankais3r/Video-Depthify

def average_images(dir_path = './depth'):
	logger(f'Averaging depth images')

	# Get the number of items in the directory minus the first and last images
	items = len(glob.glob(f'{dir_path}/*.jpg')) - 2
	first = f'{dir_path}/00000001.jpg'
	last = f'{dir_path}/' + str(items + 2).zfill(8) + '.jpg'
	w, h = Image.open(first).size

	# Create averaged folder inside dir_path if it doesn't exist
	average_dir = f'{dir_path}/averaged'
	if not os.path.exists(f'{average_dir}'):
		os.makedirs(f'{average_dir}')

	Image.open(first).save(first.replace(f'{dir_path}', f'{average_dir}'))

	# Loop through the images and average them
	for idx in range(items):
		current = idx + 2
		# arr = np.zeros((h, w, 3), np.float64)
		# arr = np.zeros((h, w, 1), np.float64)
		arr = np.zeros((h, w, 3), np.float64)

		prev = np.array(Image.open(f'{dir_path}/' + str(current - 1).zfill(8) + '.jpg').convert('RGB'), dtype = np.float64)
		curr = np.array(Image.open(f'{dir_path}/' + str(current).zfill(8) + '.jpg').convert('RGB'), dtype = np.float64)
		next = np.array(Image.open(f'{dir_path}/' + str(current + 1).zfill(8) + '.jpg').convert('RGB'), dtype = np.float64)
		
		arr = arr+prev/3
		arr = arr+curr/3
		arr = arr+next/3
		# arr = (prev + curr + next) / 3  # Add arrays element-wise
		
		arr = np.array(np.round(arr), dtype = np.uint8)
		
		out = Image.fromarray(arr,mode = 'RGB')
		out_file = f'{average_dir}/' + str(current).zfill(8) + '.jpg'
		out.save(out_file)

		logger(f'Averaging frames: {round((current / items) * 100, 1)}%', temporary=True)
		

	Image.open(last).save(last.replace(f'{dir_path}', f'{average_dir}'))
	logger(f'Averaging complete')
import numpy as np 
from astropy import units
from sunpy.time import parse_time


def read_bst_data(filename):
	"""

	"""


	f = open(filename, "rb")
	data_bytes = f.read()

	data_array = np.fromfile(filename)

	bit_mode = len(data_bytes)/len(data_array)

	num_beamlets = int(244*16/bit_mode)

	data_array_reshape = data_array.reshape(-1, num_beamlets).T